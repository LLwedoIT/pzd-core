1. Install Dependencies

pip install opencv-python numpy Pillow


2. Run the Desktop Core

python app/main.py


3. Push to GitHub (If not done)

git add .
git commit -m "feat: spatial mapping and calibration mode"
git push origin main


4. Using the VS Code Agent

Open the folder pzd-core in VS Code.

Open the Chat/Agent window (Copilot/Cursor).

Paste the contents of PROMPT_FOR_IDE_AGENT.md as your first message to set the context.

Ask: "Review app/main.py and suggest how to implement a global hotkey for the Panic-Kill feature."