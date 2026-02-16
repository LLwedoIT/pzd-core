PZD Project Architecture & Repository Structure

To support both the Python desktop application and the Netlify-hosted landing page, we will use a Monorepo structure. This keeps your branding and your logic in sync.

1. Repository Layout

/pzd-root
├── .github/                # GitHub Actions for CI/CD
│   └── workflows/
│       ├── build-app.yml    # Compiles Python to .exe / .app
│       └── deploy-web.yml   # Trigger Netlify builds
├── /app/                    # Python Application Source
│   ├── core/                # HPD and Kernel logic
│   ├── ui/                  # Tkinter / Custom styles
│   ├── assets/              # Icons and LED patterns
│   └── requirements.txt     # Python dependencies
├── /web/                    # Landing Page (Netlify Folder)
│   ├── index.html           # Main pzdetector.com site
│   ├── styles/              # Tailwind CSS
│   ├── scripts/             # Site animations (Lottie/PZ Pulse)
│   └── netlify.toml         # Netlify configuration
├── /docs/                   # Brand assets and HPD whitepapers
├── .gitignore               # CRITICAL: Exclude local dev secrets
├── LICENSE
└── README.md                # The project manifesto


2. Monorepo Security & Privacy Guards

Since you are housing both the landing page (public) and the app source in one place, we implement the following security layers:

Scoped Builds: Netlify is configured to only have access to the /web directory. It never sees or processes the logic in /app.

Secret Management: All API keys or sensitive configurations are stored in GitHub Actions Secrets and injected during the build process. They are never hardcoded in the repo.

Dependency Auditing: Use GitHub's Dependabot to automatically monitor both your Python (/app) and Web (/web) dependencies for vulnerabilities.

Branch Protection: Enable "Protected Branches" on main. This ensures that any change—whether to the website or the code—must pass automated tests before being merged.

3. CI/CD Workflow (The Netlify Plus)

The integration remains seamless:

Automatic Deploys: Connect Netlify to the /web directory. Every time you push a change to the site's copy or CSS, the site updates instantly.

Preview Deploys: Test new "Glazed Vision" animations on the site via unique branch URLs before they go live on pzdetector.com.

4. Platform Decision: Why GitHub?

GitHub Actions: Matrix Builds allow us to test the PZDetector on both Windows and macOS runners simultaneously.

Issue Tracking: Centralized feedback for the "Kitten Buffer" and "Fog Mode" features.

Releases: Host your compiled .exe and .app files securely, linked directly from your Netlify landing page.

5. Netlify Configuration (netlify.toml)

This file in your root ensures Netlify stays in its lane:

[build]
  base = "web/"
  publish = "."
  command = "echo 'Building PZD Landing Page...'"

[status]
  # Reports build status back to your GitHub PRs

Developer/BA Notes

All code comments and UI labels should now treat "Presence Zone" as a proper noun.

{
  "proprietary_term": "Presence Zone",
  "abbreviation": "PZ",
  "usage": "Presence Zone™",
  "competitor_block": "Active"
}

