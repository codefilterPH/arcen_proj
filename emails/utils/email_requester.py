import requests

class EmailRequest:
    def __init__(self, **kwargs):
        # Default values
        self.site_domain = "https://dmis.airforce.mil.ph"
        self.url = "api/send-email/account-creation-notif/"

        # Extract app_name and email from kwargs, or use defaults if not provided
        self.app_name = kwargs.get('app_name', 'Portal App')
        self.email = kwargs.get('email', 'eugenereybulahan@gmail.com')

    def send_request(self):
        # Construct the full URL with query parameters
        full_url = f"{self.site_domain}/{self.url}"
        params = {
            "email": self.email,
            "app_name": self.app_name
        }
        try:
            # Send the GET request with SSL verification disabled
            response = requests.get(full_url, params=params, verify=False)
            # Raise an error if the request was unsuccessful
            response.raise_for_status()
            return response.json()  # Return the JSON response if available
        except requests.exceptions.RequestException as e:
            # Handle errors
            print(f"An error occurred: {e}")
            return None


if __name__ == "__main__":
    try:
        # Sample usage with error handling
        email_request = EmailRequest(app_name="Portal App", email="simpleryan26.velacruz@gmail.com")
        response = email_request.send_request()

        if response:
            print("Request Successful:")
            print(response)
        else:
            print("Request Failed")
    except Exception as e:
        # Handle any other unexpected exceptions
        print(f"Unexpected error: {e}")
