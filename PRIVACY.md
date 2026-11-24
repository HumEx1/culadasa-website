# Privacy and security rule

This repository is shared on GitHub with everyone who uses or edits the Culadasa website, and it will be public. Privacy and security of every one of those people come first.

## The rule

1. **No private information about anyone who uses, edits or maintains this code base goes into the repository.** That means no email addresses, phone numbers, home or postal addresses, personal account names, login names, passwords, API keys, two-factor backup codes, private messages, or anything else that identifies or exposes a person. Names and public roles on the website itself (the teachers list, the testimonials, Culadasa's biography) are the site's published content and are fine.
2. **Credentials never go in git, in any form**: not in code, configuration, comments, commit messages, issue text or documentation. Logins for the domain, hosting, SoundCloud, YouTube and any shared account are kept in the maintenance group's private password sheet, outside this repository.
3. **If there is any doubt whether a piece of information should be recorded here, ask the person you are working with before writing it.** Do not record first and tidy later; once pushed, it is in the history.
4. **Anything found here that breaks this rule is reported to the maintenance group at once**, removed, and the exposed credential rotated. Removing a file from the latest commit is not enough; it stays in history, so treat it as leaked.

## Where private details live instead

- Contact details and who holds which access: a private document kept by the maintainers, not in this repository.
- Passwords, logins and backup codes: the maintenance group's private password sheet.

## For automated assistants

Any AI assistant or script working in this repository follows this rule as a hard constraint and asks before recording anything that might be personal.
