# Discord AI Art Bot

This is a Discord bot built using the `discord.py` library that allows users to generate AI art and claim daily credits. The bot utilizes Firebase Realtime Database for managing user data.

## Installation Guide

### Prerequisites

- **Python 3.8+**: Ensure Python is installed on your machine. You can download it from [here](https://www.python.org/downloads/).
- **Git**: Make sure Git is installed to clone the repository. You can download it from [here](https://git-scm.com/).

### Steps to Set Up

1. **Clone the GitHub repository**:
   Open your terminal and run the following command to clone the project:
   ```bash
   git clone https://github.com/wolverine-17/Discord-AI-ART-Bot.git
   cd Discord-AI-ART-Bot
   ```
2. **Install the required dependencies**:
  After cloning the repository, install the required Python packages by running:
  ```bash
  pip install -r requirements.txt
  ```
### Set up Firebase Realtime Database:

1. **Go to Firebase Console**:
   - Go to [Firebase Console](https://console.firebase.google.com/).
   
2. **Create a new project or use an existing one**:
   - If you don't have a project, create a new one. If you already have a project, select it.

3. **In the Firebase project, navigate to Realtime Database**:
   - After selecting your project, go to the **Realtime Database** section and create a new database.

4. **Go to Project Settings and generate credentials**:
   - Go to the **Project Settings** by clicking the gear icon on the left sidebar.
   - Scroll down to the **Service Accounts** tab.
   - Click **Generate New Private Key** to download the credentials file (a JSON file).

5. **Populate the `.env` file with Firebase credentials**:
   - Copy the contents of the downloaded JSON file and populate the following fields in the `.env` file:
     - `TYPE=""`
     - `PROJECT_ID=""`
     - `PRIVATE_KEY_ID=""`
     - `PRIVATE_KEY=""`
     - `CLIENT_EMAIL=""`
     - `CLIENT_ID=""`
     - `AUTH_URI=""`
     - `TOKEN_URI=""`
     - `AUTH_PROVIDER_X509_CERT_URL=""`
     - `CLIENT_X509_CERT_URL=""`
     - `UNIVERSE_DOMAIN=""`

### Prepare the `.env` file:

1. **Rename the `.env.example` file to `.env`**:
   - Once the repository is cloned, rename the `.env.example` file to `.env`.

2. **Enter the Firebase credentials**:
   - Paste the Firebase credentials from step 5 into the `.env` file in the appropriate fields.

3. **Go to the Discord Developer Portal**:
   - Visit [Discord Developer Portal](https://discord.com/developers/applications) and create a new application.

4. **Create a bot and get the Token**:
   - Under the **Bot** tab, click **Add Bot** to create your bot.
   - Copy the **Token** and add it to your `.env` file as `BOT_TOKEN`.

### Run the bot:

1. **Start the bot by running the following command in your terminal**:
   ```bash
   python main.py

## Contact

For any questions or support, feel free to contact me:

- **Discord**: [@.wolverine__17]
- **Email**: [Maile Me](mailto:kthejas18@gmail.com)

   
