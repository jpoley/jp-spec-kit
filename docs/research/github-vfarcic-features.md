# Top 10 GitHub Project Setup Tricks You MUST Use in 2025!

**Video:** [https://www.youtube.com/watch?v=gYl3moYa4iI](https://www.youtube.com/watch?v=gYl3moYa4iI)

**Video ID:** `gYl3moYa4iI`

**Playlist:** DevOps & AI Toolkit

**Description:** Tired of chaotic repositories with vague bug reports, unclear pull requests, and outdated dependencies? This video shows you how to transform any GitHub repo...

---

## Summary

### Overview

This video demonstrates how to transform chaotic GitHub repositories into well-organized projects using built-in GitHub tools and automation. The presenter addresses common frustrations: vague bug reports, unclear PRs, outdated dependencies, and security issues piling up. The solution involves issue templates, PR templates, automated workflows, and proper governance files.

### Key Topics Covered

#### 1. Issue Templates

- **Problem solved**: People filing vague "it's broken" bug reports without context
- **Solution**: Create structured forms in `.github/ISSUE_TEMPLATE/` that guide users
- **Configuration file**: `config.yaml` with `blank_issues_enabled: no` to disable default blank forms
- **Contact links**: Direct users to GitHub Discussions, documentation, support resources, and security vulnerability reporting before filing issues
- **Bug report templates**: Include fields for description, steps to reproduce, expected vs actual behavior, environment details
- **Feature request templates**: Focus on problem statements and use cases, include "willing to contribute" checkbox
- **Key insight**: Templates reveal intent - if someone circumvents the guidance, you know they're being deliberately unhelpful

#### 2. Pull Request Templates

- **Problem solved**: PRs with no context about what changed or why
- **Solution**: Add `PULL_REQUEST_TEMPLATE.md` to `.github/`
- **Template contents**: What changed and why, type of change, testing performed, documentation updates, security considerations, breaking changes, Developer Certificate of Origin
- **AI integration**: Coding agents (like Claude Code) can read and automatically fill PR templates
- **Works for both humans and AI agents**

#### 3. CODEOWNERS File

- **Problem solved**: PRs sitting unreviewed because no one is assigned
- **Solution**: Define file paths and their owners for automatic reviewer assignment
- **Format**: `* @username` for default, specific paths like `/docs @docs-team`
- **Result**: Automatic reviewer assignment based on files changed

#### 4. Automated PR Labeling

- **Purpose**: Organize release notes by category automatically
- **Configuration**: Map file paths to labels (e.g., changes to `/docs` get "documentation" label)
- **GitHub Actions workflow**: Runs on every PR to apply labels
- **Release notes**: Automatically organized into categories (features, bug fixes, documentation)

#### 5. Release Notes Configuration

- **File**: `.github/release.yml`
- **Categories**: Maps labels to release note sections (feature/enhancement -> "New Features", bug -> "Bug Fixes")
- **Exclude section**: Filter out noise like dependabot PRs

#### 6. Security Scanning with OpenSSF Scorecard

- **Purpose**: Evaluate projects against security best practices
- **Displays**: Badge in README showing security score
- **Checks**: Pinned dependencies, code review practices, security policies
- **GitHub Actions workflow**: Runs on push to main and weekly schedule
- **Outputs**: SARIF format results uploaded to GitHub code scanning dashboard
- **Best practice**: Pin action versions with full commit SHA

#### 7. Automated Dependency Updates with Renovate

- **Problem solved**: Dependencies falling months behind, security vulnerabilities accumulating
- **Solution**: Renovate automatically creates PRs for dependency updates
- **Configuration options**: Control when updates run, grouping, automerge rules
- **Example settings**: Automerge dev dependencies with patch/minor updates, group TypeScript definitions, require code owner review for major Kubernetes client updates

#### 8. Stale Issue/PR Management

- **Problem solved**: Hundreds of outdated issues cluttering the backlog
- **Solution**: GitHub Actions workflow that marks issues as stale after inactivity
- **Configuration**: Issues with no activity for 60 days marked stale, PRs after 30 days
- **Grace period**: 7 days to respond before automatic closure
- **Exclusions**: Can exempt issues with certain labels (security) or assigned to milestones

#### 9. Documentation and Governance Files

- **README.md**: Explains what the project is, problems it solves, how to get started
- **LICENSE**: Critical - code without license creates legal issues; MIT license used as example
- **CONTRIBUTING.md**: How to submit changes
- **CODE_OF_CONDUCT.md**: Establishes interaction expectations
- **SECURITY.md**: How to report vulnerabilities responsibly
- **SUPPORT.md**: Where to get help
- **Applies to both open source and internal company projects**

#### 10. DevOps AI Toolkit Automation

- **Project setup MCP tool**: Analyzes existing files and suggests what to add
- **Process**: Select scopes, answer questions (agent suggests answers from source code), files created automatically
- **One-command setup**: Instead of hours of manual configuration

### Sponsor Mention

- **JFrog Fly**: Integrates with GitHub to help find specific fixes across releases, auto-configures development environments (npm, Python, Docker). Currently in beta.

### Key Takeaways

1. All common repository chaos is preventable with GitHub's built-in tools
2. Templates structure information and reveal user intent
3. Automation eliminates manual labeling, reviewer assignment, and dependency management
4. Governance files are important for both open source and internal projects
5. AI coding agents can leverage these templates for automated PR creation
6. The DevOps AI Toolkit can automate the entire setup process

---

## Transcript

[Music]
Have you ever seen a GitHub issue that
just said it's broken with zero context
or reviewed a pull request where you had
no idea no idea what changed or why? How
many hours have you wasted chasing down
information that should have been
provided up front? Here's the reality.
Whether you're maintaining an open
source project, building internal tools,
or managing commercial software, you
face the same problem. People file vague
bug reports. Contributors submit PRs
without explaining their changes.
Dependencies fall months behind.
Security issues pile up and you're stuck
playing detective instead of building
features. But here's what most people
don't realize. All of this chaos is
preventable. GitHub has built-in tools
for issue templates, pull request
templates, automated workflows, and
community governance. The problem is
that setting all of this up manually
takes hours, and most people either
don't know these tools exist or don't
bother configuring them properly. Today,
I'm going to show you how to transform a
chaotic repository into a wellorganized
project with clear processes, automated
workflows, and proper documentation. We
will cover issue templates that force
people to provide useful information. PR
templates that make code review actually
possible, automated dependency updates,
security scanning, and all the
governance files that make collaboration
smooth. By the end of this video, you
will know exactly how to set up a good
professional repository that saves you
hours of frustration. I will show you
how to automate the entire setup process
in minutes using the DevOps AI toolkit
instead of spending hours doing it
manually. Let's start with the most
frustrating problem. Terrible, terrible
bug reports and feature requests. We'll
take a quick break here to introduce you
to Jfrog Fly, the sponsor of this video.
So, when you manage dozens or hundreds
of releases, finding a specific fix can
be painful. Was that fix released
already? Um, with fly you know instantly
it integrates directly with your GitHub
repository and understands the content
of your releases, commits, pull
requests, metadata and artifacts. Ask a
question and Fly gives you the full
picture instantly and accurately. And on
boarding, well, usually it sucks. New
dev clones the repo, runs mpm install
and nothing works. Missing tokens, wrong
registry, private packages failing. You
know the drill, right? But with Fly, you
download the app, it scans your machine
and instantly configures everything.
NPM, Python, Docker, you name it. One
click and it works. No tokens, no config
files, no guesswork. JROGFly is
currently in beta and free to use. Check
it out at the link below and see how it
fits into your workflow. Big thanks to
JROG for sponsoring this video. And now,
let's get back to the main subject.
So, how often did you get mad because
someone reported a bug or requested a
feature without explaining what the hell
what the hell it is all about? How often
do people open issues thinking that you
can read tea leaves? Whether it's open
source, internal company projects, or
commercial products, we all face the
same frustration. It's vague, it doesn't
work type of reports that waste
everyone's time. GitHub issue templates
solve this by guiding people through
structured forms, ensuring you get the
information you actually need. So let's
see how this works in practice. So
here's the problem. I cannot scream at
people for not providing information,
filing invalid issues, and doing other
things that make me go insane
if I do not provide means for them to
get informed. So the first thing they
need is an easy way to find information.
They need to be able to quickly check
whether we already discussed the feature
they would like to propose and engage in
a conversation. I need them to be able
to check the docs in case something is
already documented to see the process
for requesting support and to see what
to do in the case they believe there is
a security issue. So let me show you
what this looks like in my DevOpsi
toolkit repository. I'm opening the
issue page and clicking on the new issue
button. Now notice what appears. Instead
of just a blank issue form, I get a menu
with multiple options. There are links
to GitHub discussions for questions,
documentation, support, resources, and
security vulnerabilities reporting. This
is exactly what I was talking about
guiding people to the right place before
they even start typing. And all we have
to do is add a config yaml
togithub/issue
template with the links. That's all it
takes. The key part here is blank issue
enabled. No, which disables the default
blank issue form. Then we define contact
links that point people to the right
resources, discussions for questions,
documentation for existing info, support
resources for help, and a private
channel for security vulnerabilities.
This reduces noise in the issues and
guides people to appropriate channels
before they even consider filing an
issue. Now, let's say that someone
actually needs to report a bug. Instead
of one big description field that would
leave someone wondering what the hell to
report, we can guide them through
specific fields, a description, steps to
reproduce, expected versus sexual
behavior, environment details, and so on
and so forth. We create a form with all
those fields, mark which ones are
mandatory, provide short explanations
for each, and include helpful guidance
before they start filling it out. Now,
back in the menu, I'm clicking on bug
report. This is what the structured bug
report form looks like. Notice the
before submitting checklist at the top
guiding people to search existing issues
and check documentation first. Then
there are specific fields with clear
labels and placeholders. And here's how
it's configured. The template defines
the form structure with text area fields
for descriptions, input fields for
version numbers, and environment details
and validations marking which are
required. Each field has a clear label,
description, and placeholders showing
exactly what we need. Feature requests
follow the same pattern, but need
different information. So when someone
clicks on feature request, they get a
form focused on understanding the
problem, not just collecting a wish
list. Now notice the prominent note.
Nice to have is not the strong use case.
Please explain the specific problem this
feature would solve. That's intentional.
We want people to think about the
problem they're trying to solve, not
just ask for random features. And here's
how it's configured. This template
focuses on problem statements, use
cases, and even asks about priority with
the drop-down field. There's also a
question about whether the person is
willing to contribute the feature
themselves. The goal is to filter out
casual, hey, wouldn't it be cool if type
of requests and focus on actual problems
that need solving. Now, and this is
important, let us be clear here, issue
templates are not, and I repeat, are not
bulletproof. Someone can still ignore
the structure, delete all the fields,
and write, "Hey, it's broken anyway."
But here's the thing. If someone does
that, you will know it's not an honest
mistake. They deliberately circumvented
the guidance you provided. And at that
point, you know you're dealing with an
and you can treat the issue
accordingly. Templates don't just
structure information, they also reveal
intent.
How often did it happen that you review
a pull request only to find that you
have no idea what the hell it is all
about? How often you had no clue what
the author wanted to do, how to test it,
whether it is backwards compatible, and
so on and so forth. How often you
started a review only to start
daydreaming how much nicer your life
would be if you could fire that person
for making your job miserable. The
solution is the same as with the issues.
We need to guide people by providing the
information they need to provide to us.
For PRs, that means explaining what
changed and why, how to test it, whether
there are breaking changes, security
implications, and all the other context
that makes code review actually possible
instead of an exercise in frustration.
For all that, all we have to do is add a
pull request template markdown file to
GitHub with the structure we need. This
template covers everything you would
want to know when reviewing code. what
changed and why, which type of change it
is, testing what was done, documentation
update, security considerations, and
whether there are breaking changes.
There's even a developer certificate of
origin section for projects that require
it, and guidance on conventional comet
formatting for automated change log
generation. Now, you could fork this
repo, make some changes, and create a PR
to see the template in action. But I'm
not creating PRs manually anymore.
coding agents do that for me as part of
the development process. And that's what
I want to show you. I'm going to start a
coding agent session and use a workflow
command that tells it that I'm done with
the task and ready to create a PR. The
agent will analyze the changes,
automatically, fill out the PR template,
and create the pull request. So, let me
fire up cloud code. I'm running the
prdunk command, which is a workflow
command that handles everything needed
when development is done. running tests,
validating quality, creating comets, and
creating pull requests. The key thing
here is that it uses the PR template to
discover which information is needed,
how to format the PR, and which
additional tasks to execute. The
template works for both humans filling
out forms manually and AI agents
analyzing changes automatically. Now, I
will not go into the details of this
command right now. If you want to learn
more about it, check out uh this video
somewhere there where I explained my
whole development workflow. What matters
for this demo is showing how PR
templates guide both people and AI and
how having detailed structured
information makes reviews possible
whether they are done by humans or in my
case by code rabbit a review AI. So the
agent analyzes the changes I made, looks
at the PR template to understand what
information is needed, and proposes the
complete the complete PR content. So
let's see what it came up with. Look at
what the agent produced. A complete PR
with title following conventional commit
format, detailed description explaining
what changed and why, type of change,
manual testing performed, breaking
changes, analysis, security
considerations, and everything else the
template asked for. The agent didn't
just fill out a form. It analyzed the
actual changes and provided meaningful,
accurate information that makes the PR
reviewable. From here on, I can simply
say yes to accept it, which is what I
will do today, or I could correct it if
something needs to be changed. The agent
creates the pier and pushes it to
GitHub. So, let me open it in the
browser uh to see the results, whether
it did it right. And there it is, a
fully structured pull request with all
the information anyone reviewing it
would need. Whether that reviewer is a
human or an AI like code rabbit, it does
not matter. The template assures the
information is there complete and
properly formatted. This is what happens
when you guide people or agents through
providing the information you need
instead of hoping they will figure it
out by themselves.
Now, don't you get frustrated when a
peer is not reviewed by anyone simply
because it was not assigned to anyone.
You did all the work and then the peer
is sitting there waiting for something
to happen. What do you do? Start pinging
people to see whether anyone should
review it. Do you even know who that
someone is? The solution is code owners.
It automatically assigns reviewers based
on which files are changed. If someone
modifies code in the front end
directory, the front end team gets
assigned. If it's infrastructure
changes, the platform team gets
notified. No more guessing. No more
forgotten PRs. Now, I'm the only one
working on this project, the one I'm
using for the demo today. So, I cannot
show you automatic assignment in action
since there is no one else my PRs can be
assigned to. So, we skipping the usual
demo and jumping straight to the
configuration. The file is simple.
Define PS and their owners. The asterisk
means everything in the repo. So I'm the
default owner for all the files. You can
get more specific with pots like /docs
for the docs team or slrc/core
for the architecture team and so on and
so forth. When someone opens a PR
touching those files, the corresponding
owners get automatically requested for
review. No manual assignment needed.
None. Now let's talk about what happens
after those peers are reviewed, merged,
and released. So, wouldn't it be nice
when you take a look at release notes to
quickly discover what it's all about? Is
it a new feature or a bug fix? Is it an
update of dependencies? Is it only a
clarification in the docs? Labels can
solve that, but no one remembers to
label PRs correctly. If they would, we
could use labels to easily distinguish
work that was released. And that's where
automation comes in. We can
automatically label PRs based on the
files changed and then use those labels
to organize release notes into
categories. Let me show you what that
looks like in my releases. Please notice
the what's changed section with
categories like documentation,
organizing the changes. In the release
with more PRs, you would see sections
for new features, bug fixes,
dependencies, and so on and so forth.
But this project releases one feature at
a time. So only one in each release. And
here's the good thing. It's all
automatic based on PR labels. And here's
how the categorization is configured.
The configuration defines categories
with their corresponding labels. Pers
labeled with feature enhancement or fit
going to new features. Bug fixes going
to bug fixes. Documentation changes get
their own section. There's even an
exclude section to filter out noise like
dependency bot PRs or duplicate issues.
When you create a GitHub release, it
automatically generates organized nodes
based on those categories.
Security matters. It doesn't matter
whether you're building open source
projects or internal tools. You need to
know whether your project follows
security best practices and so do people
using it. One way to demonstrate and
track that is through security badges
and automated security scanning. Now
look at the badges at the top of the
readmi. There's an open SSF scorecard
badge showing a score of 6.1 at that
time. I improved it in the meantime. I
promise. The open SSF scorecard
evaluates projects against security best
practices. Whether you pin dependencies,
use code review, have security policies
and so on and so forth. The higher the
score, the more confidence both you and
your users have in the project security
posture. This isn't just for show. It's
automated scanning that actually checks
your repository and workflows. Here's
how it's configured. This GitHub actions
workflow runs the Open SSF scorecard
analysis on every push to the main
branch and on a weekly schedule. It
checks your repository against security
best practices, generates results in SAR
format and uploads them to GitHub's code
scanning dashboard. The workflow also
publishes results so you can display
that badge. Now notice the pinned action
versions with full comet SH. That's one
of the things the scorecard checks for.
What is the most boring and at the same
time very time consuming task you might
or might not be doing? Yep, updating
dependencies. You're either sick of
updating them all the time or you just
keep the versions you had initially. The
former must be a toy that makes you hate
yourself and the company you work in,
while the latter typically results in
someone discovering there is a security
breach in one of the dependencies
triggers a depression to those knowing
that updating years old dependencies to
fix whatever is happening is a
nightmare. It is Renovate solves this by
automatically creating PRs when new
versions are available. So let me show
you what that looks like. This is a
renovate PR updating a TypeScript
dependency. Notice it shows the change,
the age of the dependency, confidence
level, and it's already labeled with
dependencies. The PR even tells you it's
configured for automerge.
So, here's the configuration that
enabled Renovate in my repo. The
configuration controls how Renovate
behaves, when it runs, how it groups
updates, what gets automerged, and so on
and so forth. For example, dev
dependencies with patch or minor updates
get automerged automatically. TypeScript
definitions get grouped together. Major
Kubernetes client updates require review
from code owners. You control the noise
level and let automation handle the
tedious work. Now you don't need to
worry about dependency upgrades. You get
pull requests created automatically. And
all you have to do is either merge them
yourself or if you're doing things
right, let them merge automatically
because you have truly reliable tests
that will detect if something is wrong.
Now remember earlier when we talked
about organizing release nodes by
category, do you? That requires PR
labels. But who remembers to label PRs
correctly? Nobody. So we will automate
that too. Notice the labels on this PR
CI/CD and documentation. Those were
added automatically based on which files
were changed. And here's how that's
configured. The labeler configuration
maps file paths to labels. Changes to
docs get labeled documentation. Changes
to workflows get CI/CD. Changes to test
get tests and so on and so forth. The
GitHub actions workflow runs on every PR
and applies the labels automatically.
Now your release notes are organized
without anyone having to remember to add
labels manually. Finally, don't you love
having hundreds or thousands of issues?
Huh? Well, you probably don't. Only
Mazukis do. There are two ways you can
fix that. Ideally, you should close all
open issues by developing whatever they
require you to develop. That's an
unlikely option. There are always issues
that make no sense doing because
priorities changed because there's
something you thought should be done,
but you change your opinion because they
just don't make sense to do and so on
and so forth. If that is the case, as it
probably is, all you have to do is have
a process that periodically detects and
marks issues no one touched in a while
tail. Think of it as a reminder that
those you don't care about might not be
worth having. And if you keep ignoring
them, they should be deleted. Now, do
you see that bot comment? This issue has
been automatically marked as stale
because it has not had recent activity.
It will be closed if no further activity
occurs. Notice the stale label was added
automatically. If no one comments or
updates the issue within the configured
time, it gets closed. And here's how
that's configured. The workflow runs
daily checking for issues with no
activity for 60 days and peers with no
activities for 30 days. It marks them
stale, gives people 7 days to respond
and then closes them. And this is
important. The configuration accepts
issues with certain labels like security
or those assigned to milestones. You
don't want to close things that actually
need attention just because they're
waiting on maintainers. But most of the
others you do.
All the templates and workflows and
automation we covered are great, but
they mean nothing if people don't
understand what your project does or how
to use it. Projects need documentation.
And I'm not just talking about open
source. Internal projects, company
tools, anything people need to work with
requires clear documentation. So let's
walk through what that looks like. So,
what is the one place you or anyone else
goes to to find information? H where do
developers, users, contributors, or
anyone else go? I'm sure you know the
answer to that one, right? It's the
readme. It's not just for people
discovering your project for the first
time. It's also for you, the person
working on it. That's where everyone
starts. A comprehensive readme explains
what the project is, what problems it
solves, who should use it, and how to
get started. New team members, potential
users, or anyone evaluating whether to
adopt your project need this
information. Now, here's something you
probably don't think about until it's
too late. What happens if there is no
license? In many jurisdictions, code
without the license means nobody can
legally use it, modify it, or
distribute. You publish your code
thinking you're sharing it with the
world and technically you just created a
legal minefield. Even worse, if you're
at the company, someone might argue the
company owns it or contributors might
claim rights you didn't intend to give
them. It's a mess. So, do not be that
person. This project, for example, uses
the MIT license, which is permissive and
allows people to use, modify, and
distribute the code. For internal
projects, you might have different
licensing requirements. But having it
clearly stated removes ambiguity and
protects everyone involved, everyone,
not only you. Beyond the readme and
license, projects need governance files
that explain how things work, how to
contribute, what the code of conduct is,
how to report security issues, and so on
and so forth. Now, you might think
that's only for open source projects. H,
but I would argue otherwise. It should
not matter whether people are
contributing for free to an open source
project or working on it within a
company. Everyone, everyone should know
how to contribute, how to work on that
project. Those files set expectations.
The code of conduct establishes how
people should interact. Contributing
guidelines explain how to submit
changes. The security policy tells
people how to report vulnerabilities
responsively. Having this documented
prevents confusion and establishes clear
processes whether you're an open source
maintainer or you are leading a team at
a company. Finally, people need to know
how to get help. A support section in
the rhythm points people to the right
resources, where to ask questions, how
to report bugs, where to discuss ideas.
This keeps everything organized and
prevents people from opening issues when
they should be asking in discussions or
reading the docs.
Now, everything I showed you today can
be created manually. You can do it. You
could spend hours setting up issue
templates, PR templates, workflows,
governance files, and all the rest. Or
or you could automate it. That's what
the DevOps CI toolkits project setup MCP
tool does. So, let me fire up Cloud Code
again and run the setup command. The MCP
analyzes which files are already created
and suggests which ones we might want to
add. Now I already run it in this repo.
I did so I cannot show you the full
setup process but I can explain how it
works. Once you select which scopes you
would like to add, MCP returns questions
needed to populate the files and
instructs the agent to do its best to
figure out the answers based on your
source code and other information. From
there on, all you have to do is either
accept suggested answers or provide
additional information. In either case,
the files will be created and you can
push them to your repo and live happily
ever after. In this specific case, the
only file I'm missing is adopters.
That's a file listing people or
organizations using the project. Now,
speaking of which, are you using DevOps
AI toolkit? If you are and you would
like to be listed as an adopter, please
please please open and I will add you. I
would really appreciate it a lot. So try
the project setup MCP tool or any other
tool in the DevOps CI toolkit project.
Let me know what you think. Start it,
fork it, open issues, contribute. All
those templates and governance files I
just showed you, well, they're already
set up in that project ready for you to
engage with. Thank you for watching. See
you in the next one. Cheers.
Back To Top

---

*Generated using yt-fetcher CLI*
