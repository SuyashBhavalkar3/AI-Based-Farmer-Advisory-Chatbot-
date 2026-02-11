import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "@/hooks/useAuth";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { useToast } from "@/hooks/use-toast";
import { Leaf, Rocket, Lock, Clock, Smartphone, Award } from "lucide-react";

export default function Signup() {
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const { signUp } = useAuth();
  const navigate = useNavigate();
  const { toast } = useToast();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await signUp(email, password, fullName);
      navigate("/");
    } catch (error: any) {
      toast({ title: "Signup failed", description: error.message, variant: "destructive" });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-green-50 via-emerald-50 to-teal-50 dark:from-slate-950 dark:via-emerald-950 dark:to-slate-950 px-4 py-8">
      {/* Decorative elements */}
      <div className="absolute top-0 left-0 w-96 h-96 bg-green-200 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-pulse" />
      <div className="absolute bottom-0 right-0 w-96 h-96 bg-emerald-200 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-pulse" />
      
      <div className="relative z-10 w-full max-w-6xl grid md:grid-cols-2 gap-12 items-center">
        {/* Left Side - Benefits */}
        <div className="hidden md:flex flex-col gap-8 pl-6">
          <div className="space-y-4">
            <h1 className="text-5xl font-bold bg-gradient-to-r from-green-600 to-emerald-600 bg-clip-text text-transparent">
              Start Your Journey Today
            </h1>
            <p className="text-xl text-gray-600 dark:text-gray-300">
              Join thousands of farmers getting expert guidance on schemes and policies
            </p>
          </div>

          <div className="space-y-6">
            {[
              { icon: Rocket, title: "Quick Setup", desc: "Get started in under 2 minutes" },
              { icon: Lock, title: "Secure & Private", desc: "Your data is protected with encryption" },
              { icon: Clock, title: "24/7 Support", desc: "Get instant answers anytime, anywhere" },
              { icon: Smartphone, title: "Mobile Friendly", desc: "Access on any device seamlessly" },
            ].map((benefit, idx) => (
              <div
                key={idx}
                className="flex gap-4 group hover:translate-x-2 transition-transform"
                style={{
                  animation: `slideInLeft 0.6s ease-out ${idx * 0.1}s backwards`
                }}
              >
                <div className="flex-shrink-0 flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-green-500 to-emerald-600 shadow-lg group-hover:shadow-xl transition-shadow">
                  <benefit.icon className="h-6 w-6 text-white" />
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900 dark:text-white group-hover:text-green-600 dark:group-hover:text-green-400 transition-colors">
                    {benefit.title}
                  </h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400">{benefit.desc}</p>
                </div>
              </div>
            ))}
          </div>

          <div className="pt-4 border-t-2 border-green-200 dark:border-emerald-900/50 flex items-center gap-3">
            <Award className="h-5 w-5 text-green-600" />
            <p className="text-sm text-gray-600 dark:text-gray-300">
              Join 10,000+ farmers already benefiting
            </p>
          </div>
        </div>

        {/* Right Side - Signup Form */}
        <div className="flex justify-center">
          <Card className="w-full max-w-md shadow-2xl border-0 bg-white/95 dark:bg-slate-900/95 backdrop-blur">
            <CardHeader className="text-center space-y-3 pb-6">
              <div className="mx-auto mb-2 flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-green-500 to-emerald-600 shadow-lg">
                <Leaf className="h-8 w-8 text-white" />
              </div>
              <CardTitle className="text-3xl font-bold bg-gradient-to-r from-green-600 to-emerald-600 bg-clip-text text-transparent">Create Account</CardTitle>
              <CardDescription className="text-base text-gray-600 dark:text-gray-300">Join our farming community</CardDescription>
            </CardHeader>
            <form onSubmit={handleSubmit}>
              <CardContent className="space-y-5">
                <div className="space-y-3">
                  <Label htmlFor="fullName" className="text-sm font-medium text-gray-700 dark:text-gray-300">Full Name</Label>
                  <Input 
                    id="fullName" 
                    value={fullName} 
                    onChange={(e) => setFullName(e.target.value)} 
                    required 
                    placeholder="Enter your full name"
                    className="border-2 border-gray-200 dark:border-slate-700 focus:border-green-500 focus:ring-2 focus:ring-green-200 dark:focus:ring-green-900 transition-all rounded-lg px-4 py-3 bg-white dark:bg-slate-800/50"
                  />
                </div>
                <div className="space-y-3">
                  <Label htmlFor="email" className="text-sm font-medium text-gray-700 dark:text-gray-300">Email Address</Label>
                  <Input 
                    id="email" 
                    type="email" 
                    value={email} 
                    onChange={(e) => setEmail(e.target.value)} 
                    required 
                    placeholder="you@example.com"
                    className="border-2 border-gray-200 dark:border-slate-700 focus:border-green-500 focus:ring-2 focus:ring-green-200 dark:focus:ring-green-900 transition-all rounded-lg px-4 py-3 bg-white dark:bg-slate-800/50"
                  />
                </div>
                <div className="space-y-3">
                  <Label htmlFor="password" className="text-sm font-medium text-gray-700 dark:text-gray-300">Password</Label>
                  <Input 
                    id="password" 
                    type="password" 
                    value={password} 
                    onChange={(e) => setPassword(e.target.value)} 
                    required 
                    placeholder="Min 6 characters" 
                    minLength={6}
                    className="border-2 border-gray-200 dark:border-slate-700 focus:border-green-500 focus:ring-2 focus:ring-green-200 dark:focus:ring-green-900 transition-all rounded-lg px-4 py-3 bg-white dark:bg-slate-800/50"
                  />
                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">At least 6 characters for security</p>
                </div>

                <div className="flex items-start gap-2 p-3 rounded-lg bg-green-50 dark:bg-emerald-900/20 border border-green-200 dark:border-emerald-900/50">
                  <input 
                    type="checkbox" 
                    id="agree" 
                    className="w-4 h-4 cursor-pointer mt-0.5"
                    required
                  />
                  <label htmlFor="agree" className="text-xs text-gray-700 dark:text-gray-300 cursor-pointer">
                    I agree to the{" "}
                    <Link to="/terms" className="text-green-600 hover:text-green-700 dark:text-green-500 font-semibold">
                      Terms of Service
                    </Link>
                    {" "}and{" "}
                    <Link to="/privacy" className="text-green-600 hover:text-green-700 dark:text-green-500 font-semibold">
                      Privacy Policy
                    </Link>
                  </label>
                </div>
              </CardContent>
              <CardFooter className="flex flex-col gap-4 pt-6">
                <Button 
                  type="submit" 
                  className="w-full bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 text-white font-semibold py-3 rounded-lg shadow-lg hover:shadow-xl transition-all transform hover:scale-105 active:scale-95" 
                  disabled={loading}
                >
                  {loading ? (
                    <span className="flex items-center gap-2">
                      <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                      Creating account...
                    </span>
                  ) : (
                    "Sign Up"
                  )}
                </Button>

                <div className="relative flex items-center gap-3">
                  <div className="flex-1 h-px bg-gray-300 dark:bg-slate-700" />
                  <span className="text-xs text-gray-500 dark:text-gray-400">or</span>
                  <div className="flex-1 h-px bg-gray-300 dark:bg-slate-700" />
                </div>

                <p className="text-sm text-gray-600 dark:text-gray-400 text-center">
                  Already have an account?{" "}
                  <Link to="/login" className="font-semibold text-green-600 hover:text-green-700 dark:text-green-500 dark:hover:text-green-400 transition-colors">
                    Sign in here
                  </Link>
                </p>
              </CardFooter>
            </form>
          </Card>
        </div>
      </div>

      <style>{`
        @keyframes slideInLeft {
          from {
            opacity: 0;
            transform: translateX(-30px);
          }
          to {
            opacity: 1;
            transform: translateX(0);
          }
        }
      `}</style>
    </div>
  );
}
