import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { schemesAPI } from "@/services/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Loader2, ArrowLeft, Download, FileText, AlertCircle } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

interface Document {
  id: number;
  name: string;
  type: string;
  size: number;
  has_file: boolean;
  has_url: boolean;
  url?: string;
}

interface SchemeDetail {
  id: number;
  name: string;
  description: string;
  eligibility: string;
  benefits: string;
  application_process: string;
  scheme_type: string;
  documents: Document[];
  created_at: string;
}

export default function SchemeDetails() {
  const { schemeId } = useParams();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [scheme, setScheme] = useState<SchemeDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [downloading, setDownloading] = useState<number | null>(null);

  useEffect(() => {
    const fetchSchemeDetails = async () => {
      try {
        setLoading(true);
        const response = await schemesAPI.get(parseInt(schemeId!));
        setScheme(response.data);
      } catch (error: any) {
        toast({
          title: "Error",
          description: "Failed to load scheme details",
          variant: "destructive",
        });
        navigate("/schemes");
      } finally {
        setLoading(false);
      }
    };

    if (schemeId) {
      fetchSchemeDetails();
    }
  }, [schemeId, navigate, toast]);

  const handleDownloadDocument = async (doc: Document) => {
    try {
      setDownloading(doc.id);

      if (doc.has_url && doc.url) {
        // Open external URL
        window.open(doc.url, "_blank");
        toast({ title: "Success", description: "Opening document in new tab" });
      } else if (doc.has_file) {
        // Download from backend - fetch as blob
        const token = localStorage.getItem("access_token");
        const response = await fetch(
          `${import.meta.env.VITE_API_BASE_URL}/api/v1/schemes/documents/${doc.id}/download`,
          {
            method: "GET",
            headers: {
              "Authorization": token ? `Bearer ${token}` : "",
            },
          }
        );

        if (!response.ok) {
          throw new Error("Failed to download document");
        }

        // Check if it's a JSON response (for redirect_url)
        const contentType = response.headers.get("content-type");
        if (contentType?.includes("application/json")) {
          const data = await response.json();
          if (data.data?.redirect_url) {
            window.open(data.data.redirect_url, "_blank");
            toast({ title: "Success", description: "Opening document in new tab" });
            return;
          }
        }

        // Handle file download
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        link.setAttribute("download", doc.name);
        document.body.appendChild(link);
        link.click();
        link.parentNode?.removeChild(link);
        window.URL.revokeObjectURL(url);
        
        toast({ title: "Success", description: "Document downloaded successfully" });
      } else {
        toast({
          title: "Error",
          description: "No file or URL available for this document",
          variant: "destructive",
        });
      }
    } catch (error: any) {
      console.error("Download error:", error);
      toast({
        title: "Error",
        description: error?.message || "Failed to download document",
        variant: "destructive",
      });
    } finally {
      setDownloading(null);
    }
  };

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center bg-gradient-to-b from-white/40 to-green-50/20 dark:from-slate-900/40 dark:to-emerald-900/10">
        <Loader2 className="h-8 w-8 animate-spin text-green-600" />
      </div>
    );
  }

  if (!scheme) {
    return (
      <div className="flex h-screen items-center justify-center bg-gradient-to-b from-white/40 to-green-50/20 dark:from-slate-900/40 dark:to-emerald-900/10">
        <div className="text-center">
          <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
          <p className="text-gray-600 dark:text-gray-400 mb-4">Scheme not found</p>
          <Button onClick={() => navigate("/schemes")} variant="outline">
            Back to Schemes
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-screen flex-col bg-gradient-to-b from-white/40 to-green-50/20 dark:from-slate-900/40 dark:to-emerald-900/10">
      {/* Header */}
      <div className="border-b border-green-100 dark:border-emerald-900/30 bg-white/50 dark:bg-slate-900/50 backdrop-blur p-6">
        <div className="max-w-4xl mx-auto">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => navigate("/schemes")}
            className="mb-4 text-green-700 dark:text-green-400 hover:bg-green-50 dark:hover:bg-emerald-900/30"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back
          </Button>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">{scheme.name}</h1>
          <p className="text-sm text-gray-600 dark:text-gray-300 mt-2">
            Scheme Type: <span className="inline-block px-2 py-1 bg-green-50 dark:bg-emerald-900/20 text-green-700 dark:text-green-400 rounded text-xs ml-1">{scheme.scheme_type}</span>
          </p>
        </div>
      </div>

      {/* Content */}
      <ScrollArea className="flex-1">
        <div className="max-w-4xl mx-auto p-6 space-y-6">
          {/* Description */}
          <Card className="border-green-100 dark:border-emerald-900/50">
            <CardHeader>
              <CardTitle className="text-lg">Overview</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4 text-gray-700 dark:text-gray-300 leading-relaxed whitespace-pre-wrap">
              {scheme.description}
            </CardContent>
          </Card>

          {/* Eligibility */}
          {scheme.eligibility && (
            <Card className="border-green-100 dark:border-emerald-900/50">
              <CardHeader>
                <CardTitle className="text-lg">Eligibility Criteria</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4 text-gray-700 dark:text-gray-300 leading-relaxed whitespace-pre-wrap">
                {scheme.eligibility}
              </CardContent>
            </Card>
          )}

          {/* Benefits */}
          {scheme.benefits && (
            <Card className="border-green-100 dark:border-emerald-900/50">
              <CardHeader>
                <CardTitle className="text-lg">Benefits</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4 text-gray-700 dark:text-gray-300 leading-relaxed whitespace-pre-wrap">
                {scheme.benefits}
              </CardContent>
            </Card>
          )}

          {/* Application Process */}
          {scheme.application_process && (
            <Card className="border-green-100 dark:border-emerald-900/50">
              <CardHeader>
                <CardTitle className="text-lg">Application Process</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4 text-gray-700 dark:text-gray-300 leading-relaxed whitespace-pre-wrap">
                {scheme.application_process}
              </CardContent>
            </Card>
          )}

          {/* Documents */}
          {scheme.documents.length > 0 && (
            <Card className="border-green-100 dark:border-emerald-900/50">
              <CardHeader>
                <CardTitle className="text-lg">Required Documents</CardTitle>
                <CardDescription>Download all necessary documents for application</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {scheme.documents.map((doc) => (
                    <div
                      key={doc.id}
                      className="flex items-center justify-between p-4 rounded-lg border border-green-100 dark:border-emerald-900/50 hover:bg-green-50 dark:hover:bg-emerald-900/10 transition-colors"
                    >
                      <div className="flex items-center gap-3">
                        <FileText className="h-5 w-5 text-green-600 dark:text-green-400" />
                        <div>
                          <p className="font-medium text-gray-900 dark:text-white">{doc.name}</p>
                          <p className="text-xs text-gray-500 dark:text-gray-400">
                            Type: {doc.type} {doc.size ? `• Size: ${(doc.size / 1024).toFixed(2)} KB` : ""}
                          </p>
                        </div>
                      </div>
                      <Button
                        size="sm"
                        onClick={() => handleDownloadDocument(doc)}
                        disabled={downloading === doc.id}
                        className="bg-green-500 hover:bg-green-600 text-white"
                      >
                        {downloading === doc.id ? (
                          <Loader2 className="h-4 w-4 animate-spin" />
                        ) : (
                          <>
                            <Download className="h-4 w-4 mr-2" />
                            Download
                          </>
                        )}
                      </Button>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {scheme.documents.length === 0 && (
            <Card className="border-green-100 dark:border-emerald-900/50">
              <CardContent className="pt-6">
                <p className="text-center text-gray-600 dark:text-gray-400">No documents available for this scheme</p>
              </CardContent>
            </Card>
          )}
        </div>
      </ScrollArea>
    </div>
  );
}
