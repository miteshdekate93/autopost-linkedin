"""
LinkedIn API Client
Handles OAuth 2.0 token management and post publishing via the LinkedIn UGC Posts API.

Docs: https://docs.microsoft.com/en-us/linkedin/marketing/integrations/community-management/shares/ugc-post-api
"""

import os
import requests


LINKEDIN_API_BASE = "https://api.linkedin.com/v2"
TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"


class LinkedInClient:
    def __init__(self):
        self.client_id = os.environ["LINKEDIN_CLIENT_ID"]
        self.client_secret = os.environ["LINKEDIN_CLIENT_SECRET"]
        self.access_token = os.environ["LINKEDIN_ACCESS_TOKEN"]
        self.person_urn = os.environ["LINKEDIN_PERSON_URN"]

    def refresh_access_token(self) -> str:
        """
        Refresh the OAuth 2.0 access token using the stored refresh token.
        LinkedIn access tokens expire every 60 days.
        """
        refresh_token = os.environ.get("LINKEDIN_REFRESH_TOKEN")
        if not refresh_token:
            raise ValueError("LINKEDIN_REFRESH_TOKEN not set — cannot refresh token")

        response = requests.post(
            TOKEN_URL,
            data={
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
                "client_id": self.client_id,
                "client_secret": self.client_secret,
            },
        )
        response.raise_for_status()
        new_token = response.json()["access_token"]
        self.access_token = new_token
        print("✓ Access token refreshed successfully")
        return new_token

    def publish_post(self, content: str) -> dict:
        """
        Publish a text post to LinkedIn using the UGC Posts API.

        Args:
            content: The post text content (max ~3000 chars recommended)

        Returns:
            The API response with the created post ID
        """
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0",
        }

        payload = {
            "author": self.person_urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": content
                    },
                    "shareMediaCategory": "NONE",
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            },
        }

        response = requests.post(
            f"{LINKEDIN_API_BASE}/ugcPosts",
            headers=headers,
            json=payload,
        )

        # If token expired (401), try refreshing and retry once
        if response.status_code == 401:
            print("Access token expired — refreshing...")
            self.refresh_access_token()
            headers["Authorization"] = f"Bearer {self.access_token}"
            response = requests.post(
                f"{LINKEDIN_API_BASE}/ugcPosts",
                headers=headers,
                json=payload,
            )

        response.raise_for_status()
        return response.json()
