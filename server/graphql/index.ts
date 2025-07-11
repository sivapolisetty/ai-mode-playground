import { ApolloServer } from 'apollo-server-express';
import { ApolloServerPluginDrainHttpServer } from 'apollo-server-core';
import { typeDefs } from './schema';
import { resolvers } from './resolvers';
import { Express } from 'express';
import { Server } from 'http';

export async function setupApolloServer(app: Express, httpServer: Server) {
  // Create Apollo server
  const server = new ApolloServer({
    typeDefs,
    resolvers,
    plugins: [ApolloServerPluginDrainHttpServer({ httpServer })],
    context: ({ req }) => {
      // Add any context data here
      return { req };
    },
  });

  // Start the server
  await server.start();
  
  // Apply middleware
  server.applyMiddleware({ 
    app,
    path: '/api/graphql'
  });
  
  console.log(`GraphQL server ready at /api/graphql`);
  
  return server;
}
