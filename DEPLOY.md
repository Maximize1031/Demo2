# Put the demo on your website

## 1. Source repository

The application repository is https://github.com/Maximize1031/Demo2.
The owner chose a public repository for this synthetic demonstration. Application
code, skill instructions, and synthetic fixtures are public; credentials and
runtime case data are excluded by `.gitignore`.

Only this application's files belong in the repository, not the parent Box folder.
For future command-line updates, authenticate Git for GitHub and push to `main`.
The connected GitHub tools can also publish updates without local Git credentials.

## 2. Create the Render service

1. Sign into https://dashboard.render.com and connect your GitHub account.
2. Choose **New → Blueprint** and select `Maximize1031/Demo2`.
3. Review `render.yaml`: it provisions one **paid** Python web service and a
   1 GB persistent disk. Confirm the prices Render displays before proceeding.
4. Set `DEMO_PASSWORD` to a random password of at least 16 characters.
5. Set `OPENAI_API_KEY` privately in Render. For a rehearsal-only deployment,
   omit/leave this value empty; if the Blueprint form requires an entry, create
   the web service manually with the same settings and omit this variable.
6. Keep `APP_ENV=production`, `DATA_DIR=/var/data`, and **one** Uvicorn worker.
7. Deploy. Render provides an HTTPS URL. Open it and sign in.

The production app refuses to start without a strong demo password. It stores
only a hash of each random session token, and sets Secure/HttpOnly/SameSite cookies.
The password and API key stay in Render's environment settings.

## 3. Verify the hosted demo

- Open the service URL and confirm the sign-in screen appears.
- Run the initial rehearsal: 19 on file / 5 external / 1 internal.
- Add the next batch: 22 on file / 1 external / 1 internal.
- Review Evidence and both drafts; confirm no escrow follow-up remains.
- Download the review, inspect History, and reset.
- In a second private browser session, confirm the case starts independently.
- With API credentials configured, run Live AI and verify its evidence and
  drafts manually. API/model/tool access still needs this real smoke test.
- Redeploy and confirm completed sessions survive on the persistent disk.

## 4. Add your domain

In the web service settings, add a custom domain, such as a `demo` subdomain of
your business domain. Follow the exact DNS record instructions Render displays
at that time. Keep the Render URL until DNS and HTTPS are working.

## Troubleshooting

- **Startup rejects the password:** set `DEMO_PASSWORD` to at least 16 characters.
- **Live AI is unavailable:** add a valid `OPENAI_API_KEY` and restart/redeploy.
- **API access declined:** check API billing, project key permissions, model
  availability, and hosted shell access.
- **Review interrupted:** retry after a restart. Prior completed revisions remain.
- **Session disappears on deploy:** confirm `DATA_DIR=/var/data` and the disk mount.
- **Questions unavailable in rehearsal:** expected. Rehearsal is labeled saved
  output; fresh assistant answers require a live review.

Never paste secrets into GitHub issues, commit messages, or chat.
