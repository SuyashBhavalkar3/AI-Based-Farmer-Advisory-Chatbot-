// ============================================
// API Client Configuration
// ============================================

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

// ============================================
// Fetch Wrapper with Request/Response Interceptors
// ============================================

class APIClient {
  private baseURL: string;

  constructor(baseURL: string) {
    this.baseURL = baseURL;
  }

  private getHeaders(isFormData: boolean = false) {
    const headers: HeadersInit = {
      ...(isFormData ? {} : { "Content-Type": "application/json" }),
    };

    const token = localStorage.getItem("access_token");
    if (token) {
      headers.Authorization = `Bearer ${token}`;
    }

    return headers;
  }

  private async handleResponse(response: Response) {
    console.log(`[API] Response status: ${response.status}, OK: ${response.ok}`);
    
    // Handle 401 Unauthorized - redirect to login
    if (response.status === 401) {
      localStorage.removeItem("access_token");
      localStorage.removeItem("user");
      window.location.href = "/login";
      throw new Error("Unauthorized - Redirecting to login");
    }

    if (!response.ok) {
      let errorMessage = "An error occurred";
      try {
        const errorData = await response.json();
        errorMessage = errorData.detail || errorMessage;
      } catch {
        errorMessage = response.statusText || errorMessage;
      }
      const error = new Error(errorMessage);
      (error as any).status = response.status;
      throw error;
    }

    try {
      const data = await response.json();
      console.log(`[API] Response data:`, data);
      return data;
    } catch (e) {
      console.error(`[API] Failed to parse response:`, e);
      return null;
    }
  }

  async get(endpoint: string) {
    const response = await fetch(`${this.baseURL}${endpoint}`, {
      method: "GET",
      headers: this.getHeaders(),
    });
    return this.handleResponse(response);
  }

  async post(endpoint: string, data?: any, isFormData: boolean = false) {
    console.log(`[API] POST ${this.baseURL}${endpoint}`, {
      isFormData,
      data: isFormData ? "(FormData)" : data,
      token: localStorage.getItem("access_token") ? "✓ Present" : "✗ Missing"
    });
    
    const response = await fetch(`${this.baseURL}${endpoint}`, {
      method: "POST",
      headers: this.getHeaders(isFormData),
      body: isFormData ? data : JSON.stringify(data),
    });
    
    console.log(`[API] POST ${endpoint} - Status: ${response.status}`);
    return this.handleResponse(response);
  }

  async delete(endpoint: string) {
    const response = await fetch(`${this.baseURL}${endpoint}`, {
      method: "DELETE",
      headers: this.getHeaders(),
    });
    return this.handleResponse(response);
  }
}

const apiClient = new APIClient(API_BASE_URL);

// ============================================
// Auth API Methods
// ============================================

export const authAPI = {
  signup: async (email: string, password: string, fullName: string) => {
    return apiClient.post("/api/v1/auth/signup", {
      email,
      password,
      full_name: fullName,
    });
  },

  login: async (email: string, password: string) => {
    return apiClient.post("/api/v1/auth/login", {
      email,
      password,
    });
  },

  getCurrentUser: async () => {
    return apiClient.get("/api/v1/auth/me");
  },

  logout: async () => {
    return apiClient.post("/api/v1/auth/logout");
  },
};

// ============================================
// Conversations API Methods
// ============================================

export const conversationsAPI = {
  list: async (limit: number = 50, offset: number = 0) => {
    const query = new URLSearchParams({
      limit: limit.toString(),
      offset: offset.toString(),
    });
    return apiClient.get(`/api/v1/conversations/?${query.toString()}`);
  },

  create: async (title: string, language: string = "en") => {
    return apiClient.post("/api/v1/conversations/", {
      title,
      language,
    });
  },

  get: async (conversationId: number) => {
    return apiClient.get(`/api/v1/conversations/${conversationId}`);
  },

  delete: async (conversationId: number) => {
    return apiClient.delete(`/api/v1/conversations/${conversationId}`);
  },
};

// ============================================
// Advisory/Query API Methods
// ============================================

export const advisoryAPI = {
  ask: async (
    question: string,
    conversationId: number,
    language: string = "en",
    includeSchemes: boolean = false
  ) => {
    return apiClient.post("/api/v1/advisory/ask", {
      question,
      conversation_id: conversationId,
      language,
      include_schemes: includeSchemes,
    });
  },

  askWithDocument: async (
    question: string,
    conversationId: number,
    language: string,
    file: File
  ) => {
    const formData = new FormData();
    formData.append("question", question);
    formData.append("conversation_id", conversationId.toString());
    formData.append("language", language);
    formData.append("file", file);

    return apiClient.post(
      "/api/v1/advisory/ask-with-document",
      formData,
      true // isFormData flag
    );
  },
};

// ============================================
// Type Definitions
// ============================================

export interface AuthResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: {
    id: number;
    email: string;
    full_name: string;
  };
}

export interface Conversation {
  id: number;
  title: string;
  language: string;
  created_at: string;
  updated_at: string;
}

export interface ConversationWithMessages extends Conversation {
  messages: Message[];
}

export interface Message {
  id: number;
  content: string;
  role: "user" | "assistant";
  created_at: string;
  conversation_id: number;
}

export interface AdvisoryResponse {
  response: string;
  original_language: string;
  context_used: boolean;
  schemes?: unknown[];
}

export default apiClient;
