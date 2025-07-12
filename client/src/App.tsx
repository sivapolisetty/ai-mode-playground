import { Switch, Route } from "wouter";
import { queryClient } from "./lib/queryClient";
import { QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";
import { ApolloProvider } from '@apollo/client';
import apolloClient from './lib/apollo-client';
import Home from "@/pages/home";
import AdminPage from "@/pages/admin";
import IntelligentUIPage from "@/pages/intelligent-ui";
import DynamicUITest from "@/components/ui/dynamic-ui-test";
import NotFound from "@/pages/not-found";

function Router() {
  return (
    <Switch>
      <Route path="/" component={Home} />
      <Route path="/admin" component={AdminPage} />
      <Route path="/intelligent-ui" component={IntelligentUIPage} />
      <Route path="/ui-test" component={DynamicUITest} />
      <Route component={NotFound} />
    </Switch>
  );
}

function App() {
  return (
    <ApolloProvider client={apolloClient}>
      <QueryClientProvider client={queryClient}>
        <TooltipProvider>
          <Toaster />
          <Router />
        </TooltipProvider>
      </QueryClientProvider>
    </ApolloProvider>
  );
}

export default App;
