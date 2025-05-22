    async def VerifyOAuthToken(self, request: auth_service_pb2.OAuthRequest, context: ServicerContext) -> auth_service_pb2.AuthResponse:
        """
        Verify an OAuth2 token and return the user and access token.
        
        Args:
            request (auth_service_pb2.OAuthRequest): OAuth token verification request
            context (ServicerContext): gRPC context
            
        Returns:
            auth_service_pb2.AuthResponse: Authentication response
        """
        try:
            user, token = await self.auth_service.verify_oauth_token(request.provider, request.token)
            
            if not user or not token:
                context.set_code(grpc.StatusCode.UNAUTHENTICATED)
                context.set_details('Invalid OAuth token')
                return auth_service_pb2.AuthResponse()
            
            return auth_service_pb2.AuthResponse(
                user=auth_service_pb2.User(
                    id=user.id,
                    email=user.email,
                    display_name=user.display_name,
                    photo_url=user.photo_url,
                    is_active=user.is_active,
                    is_verified=user.is_verified
                ),
                access_token=token
            )
            
        except Exception as e:
            logger.error(f"OAuth token verification failed: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details('Internal server error')
            return auth_service_pb2.AuthResponse()

    async def GetOAuthUrl(self, request: auth_service_pb2.OAuthUrlRequest, context: ServicerContext) -> auth_service_pb2.OAuthUrlResponse:
        """
        Get OAuth2 authorization URL for the specified provider.
        
        Args:
            request (auth_service_pb2.OAuthUrlRequest): OAuth URL request
            context (ServicerContext): gRPC context
            
        Returns:
            auth_service_pb2.OAuthUrlResponse: OAuth2 authorization URL
        """
        try:
            url = self.auth_service.get_oauth_url(request.provider)
            return auth_service_pb2.OAuthUrlResponse(url=url)
            
        except ValueError as e:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(str(e))
            return auth_service_pb2.OAuthUrlResponse()
            
        except Exception as e:
            logger.error(f"Failed to get OAuth URL: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details('Internal server error')
            return auth_service_pb2.OAuthUrlResponse()