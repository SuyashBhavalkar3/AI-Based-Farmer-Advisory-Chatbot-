import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { schemesAPI } from "@/services/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Loader2, Leaf, Droplet, TrendingUp, DollarSign, Sprout, Zap } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

interface Scheme {
  id: number;
  name: string;
  description: string;
  scheme_type: string;
  created_at: string;
}

export default function Schemes() {
  const [schemes, setSchemes] = useState<Scheme[]>([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();
  const { toast } = useToast();

  useEffect(() => {
    const fetchSchemes = async () => {
      try {
        setLoading(true);
        const response = await schemesAPI.list();
        setSchemes(response.data?.schemes || []);
      } catch (error: any) {
        toast({
          title: "Error",
          description: "Failed to load schemes",
          variant: "destructive",
        });
      } finally {
        setLoading(false);
      }
    };

    fetchSchemes();
  }, [toast]);

  const getSchemeIcon = (type: string) => {
    const icons: Record<string, React.ReactNode> = {
      "Income Support": <DollarSign className="h-6 w-6" />,
      "Insurance": <Zap className="h-6 w-6" />,
      "Credit": <TrendingUp className="h-6 w-6" />,
      "Infrastructure": <Droplet className="h-6 w-6" />,
      "Organic Farming": <Sprout className="h-6 w-6" />,
      "Agricultural Development": <Leaf className="h-6 w-6" />,
    };
    return icons[type] || <Leaf className="h-6 w-6" />;
  };

  const handleViewDetails = (schemeId: number) => {
    navigate(`/schemes/${schemeId}`);
  };

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center bg-gradient-to-br from-green-50 via-emerald-50 to-teal-50 dark:from-slate-950 dark:via-emerald-950 dark:to-slate-950">
        <Loader2 className="h-8 w-8 animate-spin text-green-600" />
      </div>
    );
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-green-50 via-emerald-50 to-teal-50 dark:from-slate-950 dark:via-emerald-950 dark:to-slate-950 px-4 py-8">
      {/* Decorative elements */}
      <div className="absolute top-0 left-0 w-96 h-96 bg-green-200 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-pulse" />
      <div className="absolute bottom-0 right-0 w-96 h-96 bg-emerald-200 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-pulse" />
      
      <div className="relative z-10 w-full max-w-6xl grid md:grid-cols-2 gap-12 items-start">
        {/* Left Side - Information */}
        <div className="hidden md:flex flex-col gap-8 pl-6">
          <div className="space-y-4">
            <h1 className="text-5xl font-bold bg-gradient-to-r from-green-600 to-emerald-600 bg-clip-text text-transparent">
              Government Schemes
            </h1>
            <p className="text-xl text-gray-600 dark:text-gray-300">
              Explore subsidies, insurance, and support programs designed to help farmers grow their business
            </p>
          </div>

          <div className="space-y-6">
            {[
              { Icon: DollarSign, title: "Income Support", desc: "Direct financial assistance to farmers" },
              { Icon: Zap, title: "Insurance Coverage", desc: "Protect your crops against unforeseen events" },
              { Icon: TrendingUp, title: "Credit Facilities", desc: "Easy access to affordable farming loans" },
              { Icon: Droplet, title: "Irrigation Aid", desc: "Infrastructure for assured water supply" },
              { Icon: Sprout, title: "Organic Farming", desc: "Support for sustainable agriculture" },
              { Icon: Leaf, title: "Development Programs", desc: "Accelerated growth opportunities" },
            ].map((item, idx) => (
              <div
                key={idx}
                className="flex gap-4 group hover:translate-x-2 transition-transform"
                style={{
                  animation: `slideInLeft 0.6s ease-out ${idx * 0.1}s backwards`
                }}
              >
                <div className="flex-shrink-0 flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-green-500 to-emerald-600 shadow-lg group-hover:shadow-xl transition-shadow text-white">
                  <item.Icon className="h-6 w-6" />
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900 dark:text-white group-hover:text-green-600 dark:group-hover:text-green-400 transition-colors">
                    {item.title}
                  </h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400">{item.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Right Side - Schemes Grid */}
        <div className="space-y-6">
          <div className="md:hidden space-y-3">
            <h1 className="text-3xl font-bold bg-gradient-to-r from-green-600 to-emerald-600 bg-clip-text text-transparent">
              Government Schemes
            </h1>
            <p className="text-gray-600 dark:text-gray-300">
              Explore subsidies, insurance, and support programs
            </p>
          </div>

          {schemes.length === 0 ? (
            <Card className="border-green-100 dark:border-emerald-900/50 bg-white/50 dark:bg-slate-900/50 backdrop-blur">
              <CardContent className="pt-12 pb-12">
                <div className="flex flex-col items-center justify-center text-center">
                  <Leaf className="h-12 w-12 text-gray-300 dark:text-gray-600 mb-4" />
                  <p className="text-gray-600 dark:text-gray-400">No schemes available</p>
                </div>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-4 max-h-[calc(100vh-200px)] overflow-y-auto pr-2">
              {schemes.map((scheme, idx) => (
                <Card
                  key={scheme.id}
                  className="border-green-100 dark:border-emerald-900/50 hover:shadow-lg transition-all cursor-pointer group overflow-hidden bg-white/50 dark:bg-slate-900/50 backdrop-blur hover:bg-white/70 dark:hover:bg-slate-900/70"
                  onClick={() => handleViewDetails(scheme.id)}
                  style={{
                    animation: `slideInLeft 0.5s ease-out ${idx * 0.1}s backwards`
                  }}
                >
                  <CardHeader className="pb-3">
                    <div className="flex items-start justify-between gap-3">
                      <div className="flex-1">
                        <CardTitle className="text-lg line-clamp-2 group-hover:text-green-700 dark:group-hover:text-green-400 transition-colors">
                          {scheme.name}
                        </CardTitle>
                        <CardDescription className="text-xs mt-2">
                          <span className="inline-flex items-center gap-1 px-2 py-1 bg-green-50 dark:bg-emerald-900/20 text-green-700 dark:text-green-400 rounded-full text-xs font-medium">
                            {getSchemeIcon(scheme.scheme_type)}
                            {scheme.scheme_type}
                          </span>
                        </CardDescription>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent className="pt-0">
                    <p className="text-sm text-gray-600 dark:text-gray-400 line-clamp-2 mb-3 leading-relaxed">
                      {scheme.description}
                    </p>
                    <Button
                      variant="outline"
                      size="sm"
                      className="w-full border-green-200 dark:border-emerald-800 hover:border-green-500 hover:bg-green-50 dark:hover:bg-emerald-900/30 text-green-700 dark:text-green-400 group-hover:bg-green-50 dark:group-hover:bg-emerald-900/20 transition-colors"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleViewDetails(scheme.id);
                      }}
                    >
                      View Details →
                    </Button>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </div>
      </div>

      <style>{`
        @keyframes slideInLeft {
          from {
            opacity: 0;
            transform: translateX(-20px);
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
