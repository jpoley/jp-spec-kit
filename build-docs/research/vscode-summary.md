# The Ultimate Agent Mode Tutorial in VS Code: Vision, MCP, Custom Agents & More!

**Video:** [https://www.youtube.com/watch?v=5NxGqnTazR8](https://www.youtube.com/watch?v=5NxGqnTazR8)

**Video ID:** `5NxGqnTazR8`

**Description:** Build a full app to budget & learn finance in VS Code using Agent Mode, Copilot Vision, MCP, BYOK, custom agents and more. Watch me go from spreadsheet → wor...

---

## Summary

### Key Points

1. **VS Code has four distinct chat modes**, each with different levels of autonomy:
   - **Ask Mode** (default): For asking questions and getting answers
   - **Edit Mode**: Performs tasks but requires user to accept and review each change
   - **Agent Mode**: Executes tasks autonomously back-to-back without individual approvals
   - **Plan Mode**: Creates detailed implementation plans without modifying code

2. **Copilot Vision** allows attaching images/screenshots to chat for visual analysis - useful for:
   - Analyzing existing designs (e.g., spreadsheets) to inspire new apps
   - Debugging by sending screenshots of problems
   - Getting AI to interpret visual elements

3. **Agent Mode capabilities:**
   - Detects when tasks take too long and asks if you want to continue waiting
   - Can pick up where it left off after interruptions
   - Prompts for permission on major actions (e.g., installing dependencies)
   - Collapses detailed explanations to save screen space while keeping them accessible

4. **Custom Agents:**
   - Allow control over agent behavior with defined name, description, tools, handoffs, and instructions
   - A "Plan" agent comes configured by default
   - Custom agents created by others are available on GitHub
   - Created via: dropdown menu > "Configure Custom Agents" > "Create New Custom Agent"

5. **Chat Participants** extend chat with domain expertise:
   - `@vscode` - has knowledge about VS Code and extension APIs
   - `@workspace` - answers project-specific questions (not generic responses)

6. **Context specification in Chat:**
   - Use `#` followed by filename to specify context (e.g., `#app.tsx`)
   - Can add files, images via "Add Context" button or drag-and-drop

7. **MCP (Model Context Protocol):**
   - Provides access to external tools for the agent
   - MCP servers appear in the tools list once installed
   - **GitHub MCP server** (official) can be installed from VS Code marketplace
   - Enables creating GitHub issues directly from chat

8. **Source Control Integration:**
   - Initialize repository from Source Control panel
   - Stage files with the plus icon ("A" indicates staged)
   - **AI-generated commit messages** available via icon next to commit input
   - Publish directly to GitHub (public or private)

9. **GitHub Integration features:**
   - View pull requests and issues via GitHub extension
   - Assign issues to Copilot (right-click > assign to coding agent)
   - GitHub Copilot Cloud Agent picks up assigned tasks in agent sessions

10. **Additional Features:**
    - **Simple Browser**: View running app within VS Code (Command Palette > "Simple Browser")
    - **DOM inspection**: Click elements to attach DOM info + screenshot to chat
    - **Bring Your Own Key (BYOK)**: Add custom models
    - **Model visibility management**: Hide/show models in the picker
    - **VS Code Speech extension**: Enables microphone input
    - **Agent Sessions**: History of all agent sessions accessible from sidebar

### How the Technologies Work

| Technology | How It Works |
|------------|--------------|
| **Agent Mode** | Executes tasks autonomously, handles dependencies, detects timeouts, prompts for permission on major actions |
| **Copilot Vision** | Accepts image attachments in chat; AI analyzes visual content and can act on it |
| **Custom Agents** | JSON-configured agents with defined tools, handoffs, and behavioral instructions stored in VS Code |
| **Chat Participants** | Domain-specific experts invoked with @ prefix that provide specialized knowledge |
| **MCP** | Protocol allowing agents to access external tools; servers installed via marketplace appear in tools list |
| **Plan Mode** | Generates detailed implementation plans as prompt files that can be edited before execution |

### Follow-up References

- **VS Code Docs** - mentioned for more details on chat features (Ask, Edit, Agent modes)
- **GitHub** - location where custom agents created by others can be found
- **VS Code Marketplace** - search "@MCP" to find MCP servers like the official GitHub MCP server
- **GitHub Copilot Cloud Agent** - for viewing and managing assigned coding tasks

---

## Transcript

Agent mode and VS code has
evolved quickly, and there's
also been a lot of new features
such as Copilot, vision, bring
your own key, MCP integration,
and more.
In today's video, I'm going to
be showing you how Agent Mode
can be used in your own custom
way with all these features,
while building a budgeting app
one that not only helps you
track your finances, but also
increases your financial
knowledge.
So let's go ahead and take a
look.
Now this video is about agent
mode, and to access it, you can
click on the chat icon right
above here.
And you'll notice right over
here within chat.
By default it's an ask mode
which is used so that we could
just ask it any question and
chat will answer.
And then there's edit mode which
chat then performs several tasks
that you ask it to do.
But you do need to accept and
review through prompts.
And then there's Agent Mode,
which does everything back to
back Autonomously, and plan
allows us to plan our features
and we will see that in action
later.
For more details on these
features, you can check out the
VS Code docs right over here.
Now within here, you'll see that
there's an option where you
could choose different models.
Right now it's on GPT five, but
there's several others we could
choose from.
And there's also a microphone
that you'll see displayed if you
have the VS Code speech extension
installed.
And then there's the send button
within here.
Also, you can add attachments
such as code or even visual
images by using a feature called
Copilot Vision.
So why don't we use a
combination of these features
such as Copilot Vision and Ask
Mode right now to kick things
off?
Lately I've been thinking about
finance and how to better manage
my budget, so I thought a good
exercise would be to create a
budgeting app.
So I'm going to ask copilot to
take a look at how this
spreadsheet looks, because it's
what I've used in the past, and
I'd like my app to be inspired
by it.
So I'll take a screenshot of
this summary here and also this
transaction sheet.
The transaction sheet has my
expenses and income with
fabricated numbers, so don't
judge me.
And the summary sheet shows how
much I've spent and how much I
can save.
But let's ask copilot what it
sees in this image.
What do you see in these two
images?
And look at that.
It gives a detailed summary of
how it interprets what it sees
in the images.
And now I'm just going to ask it
to write me a prompt so that I
could create a budgeting app,
because I think it could
probably write a prompt better
than I can.
So let me do that.
And that would be useful to do
in ask mode.
Can you go ahead and write me a
prompt that I can use to create
me a simple budgeting app that's
inspired by the images that you
saw, that allows me to enter in
my income and expenses, and then
give me a summary of how much
money I could end up saving and
a chart and look at that within
a few seconds.
It wrote this detailed prompt
here that I'm going to copy and
paste, and then we're going to
switch over to edit mode to see
what comes out after running
this.
All right.
So I've navigated to a blank
folder for a budget app before
we try to execute our prompt.
And I've also switched to edit
mode.
Let me paste our prompt at the
very beginning of the prompt, I
want to make sure that I specify
that it is a clean, modern,
responsive app and I won't
change anything else.
And let's see how it works.
All right, let's keep the work
that it's put together.
And now I'm going to ask it to
run this app.
And note that I did switch to
agent mode.
Now for major moves that it
needs to make, like installing
some dependencies.
It'll prompt me to allow, which
is okay, but at least it knows
the stuff it needs to take in
order to install the
dependencies.
Now, the other thing that's
beautiful about agent mode is if
a task is taking too long, it
could detect it and then ask you
if you want to continue waiting
like it just did.
But if the task picks up where
it needed to continue from,
Agent Mode will realize that as
it just did now, and it says,
okay, do you want to run this
command right now?
And I'll say allow.
And now it just told me that the
app is running on this port.
So if we go over here and open
up this port, let's see how it
looks.
Now, since I'm not seeing
anything, I'm going to tell
Agent Mode that I'm not seeing
anything.
Blank screen.
And in fact, I could give it a
screenshot of my problem and
drop it in, just like we did
earlier on.
And so this brings us to the
topic of debugging how easy it
is to debug with agent mode in
conjunction with Copilot vision.
Collecting projects to diagnose
why the screen is blank.
Implementing necessary updates.
And this is pretty cool right
here.
How instead of like taking up
all the realty of the chat with
all the explanation of what's
going on, it explained it and
collapsed it, but I could go
back and just see exactly what
it's doing behind the scenes and
then just collapse this again,
or I adjusted the screen just so
we could see both side by side.
Now it's giving me the option to
run and build.
All right.
And after accepting a few
changes that it provided, we now
have a visual of our budgeting
app.
All right.
So let's play around with the
app that it built for us.
So I see that I have my starting
balance here and then got some
additional income minus some
expenses.
And this would be the ending
balance.
And that seems right.
So let's say I want to click on
add over here.
Click the add button.
Doesn't seem to be doing
anything I see.
I could modify this and that
updates the numbers right away.
I'll bring that back to five
hundred, but actually it looks
like I can.
Yeah, I see if let's put in a
description here.
We'll put cable.
Now we'll put auto
transportation and I'll put five
hundred.
Now can we add.
Yes.
We're able to add that.
Although maybe I should have
named this Uber as if it was
like a side gig.
If I put in an expense cable
utility one hundred and add.
There you go.
Pretty cool.
So that seems pretty cool.
And there are some changes we
could probably add to this, such
as like making this editable so
that I could like delete line
items that I don't want.
And maybe I'd like some
graphical chart that shows the
expenses versus incomes.
So for now, let's assume that
we're okay with the way the app
is working, but we want to make
sure that the code is
understandable, and we want to
add some documentation to that.
Let's take a look at that next.
So if we were to look at our
code here on app SE, we could
see that the code looks nice and
organized, but there's not too
many comments.
So what I could do is go to chat
and simply say, hey, can you
document with comments all of.
And by using the hashtag, I
could then specify the context
that I want and select app dot
TSX.
Also notice that there's the
button here to add context and
this is where we could add
files, images, or just simply
drag and drop.
So when I click the send button
it goes straight to work.
And there you go.
You can see that it added some
detailed comments starting right
from the very beginning and
throughout the code, which is
great because if you're working
with a junior developer or even
a senior developer that has been
on vacation and they haven't
seen the code in a while,
additional comments like this
helps immensely.
Now, within chat, there is a
concept of participants which
extends the chat as a domain
specific expert.
So if I have questions about VS
code, I can use the add vs code
participant which has knowledge
about VS code and its extension
APIs.
Likewise, if I have questions
about my project, I use the At
workspace participant because it
can answer questions about my
project.
The response will be more
specific to my local situation
and not generic.
So for example, we can ask it
within our workspace to explain
how the code in our active
editor works.
So in addition to the comments
that we have can come over here
and get summarizations of
different sections of the code.
So for example, in our comments
here, we have a little verbiage
regarding what add transaction
does.
But over here there's much more
detailed information regarding
the transaction function.
Now, while I can appreciate how
it explained the way my code is
working and very straightforward
manner, I do want to mention
that I could ask it to have a
little bit more personality by
saying to explain this using
humor and emojis, and it's just
an example of how you can
customize Responses and look at
that, although it did go a
little while, including emojis
inside the code, which is not
exactly what I meant.
I just met in the explanations I
meant explain using humor and
emojis in your explanation, not
in the actual code.
So undo that.
And there you go.
I'd like to turn our attention
now to the concept of custom
agents.
Custom agents allow you to
control how the agent behaves,
and in fact, they've gotten so
popular that we even have a
location here on GitHub where
you can find many other custom
agents that were created by
others.
And if you want to create one,
you can go ahead and click on
the drop down where we have our
option for agent Ask and Edit
and you'll see an option for
configuring custom agents.
And in fact there is an agent
that has been set up that's
called plan by default, and you
can see how that one was
configured by going to configure
custom agents and then just
clicking on plan.
And you can see the structure of
it where you define the name,
the description, the tools that
it has, access to the handoffs,
and then the detailed
instructions of how that
planning agent should behave.
So you can go ahead and create
your own simply by going to
configure custom agents,
selecting Create New Custom
agent.
And then at this point I can go
ahead and choose User Data.
Give it a name.
And let's say it was for
research purposes.
And at that point I could give
it the tools that I wanted to
use and then define a
description of how it should
behave.
And when I save my research.
Agent, you could see that it
appears right here.
But let's go ahead and remove
that.
And what I want to use.
Is the one that came by default,
which is the planning agent.
And we're going to do that.
So we could add a feature to our
app.
So I'll select that.
And then I'm going to ask it to
create a feature that adds a tip
of the day button, which will
give me some type of financial
knowledge to help me become more
savvy with budgeting, investing
and overall finance and add it
to the interface.
And I'll submit that and it will
get to work.
So what's great here is it's
going to create a detailed plan
and not touch any of my code
because we are in a planning
stage.
And there I could see all the
steps that it created.
And at this point I have the
option to start the
implementation.
Or I could open it up in an
editor.
And what that's going to do is
generate a prompt file with the
plan details.
And here it is.
And I could choose to keep this.
And if I want, I can go in and
modify it and refine it to my
liking.
But it looks okay the way it is
now, so I'm not going to make
any changes.
And if I navigate to the top,
I'll see that I have an option
to either run this prompt in a
new chat or run the prompt in
the current chat.
If I decide not to do it now, I
can always go to my agent
sessions, which is right over
here where I can see all the
different agent sessions that I
have access to.
As you can see, there's a
history of them.
But for now, what I'm going to
do is close that.
So let's say I'm ready to run
this and I'm going to run it in
the current chat.
So let's go ahead to the top and
select that option prompt and
current chat.
And now it's going to go ahead
and start implementing the tip
of the day feature that I asked
for it.
I'll keep the changes that it's
making and allow it to build.
and it provides me a summary of
the work that it did to add this
feature.
Now I'll go ahead and close my
prompt file and in the terminal.
I'll run my app to see the
results.
Let's take a look.
And there you go.
At the very top.
Today's tip build financial
literacy one small concept at a
time.
Click the button to reveal
today's curated learning bite.
Using a high yield savings
account, idle cash for near term
goals should earn competitive
interest instead of sitting at a
zero percent checking account.
All right, not bad.
Let's click.
Another tip.
We can learn about what zero
based budgeting is.
And then there's an action step.
Pretty cool.
So not only do you have a budget
app now, but you could also
learn at the same time.
So now let's talk about source
control.
I have all this code locally
right now, but let's say I
wanted to push it all up to
GitHub.
Well, the first thing I'll want
to do is just make sure that I
am logged on to my GitHub
account, which you could check
from the account icon right
here.
And then just go ahead and click
on the source control icon on
the left hand side here.
And to kick things off, we could
just simply initialize our
repository.
Now we see all our files that
are currently on track.
But to go ahead and stage them
all, all I need to do is go up
to here and hit the plus icon
above all the files.
And now the letter A indicates
that they've been staged.
Now at this point I'm ready to
commit.
But what's really nice is if you
look at the icon here to the
right, we have the option to
generate a commit message
automatically with AI.
And once I click it, let's see
what it puts together for me.
And we get this nice detailed
explanation which is pretty
cool.
And I'll go ahead and now click
commit.
Once I'm done committing I can
go ahead here and publish.
And I'll like my repository to
be public and to the bottom
right hand corner.
I have an option to just open it
up in GitHub right here.
And there we go with some
documentation description of our
tech stack and steps for getting
started.
Now, while I could appreciate
that we can take some of these
steps here within source control
in VS code, we don't always have
to do everything manually.
And we could leverage MCP, which
stands for Model Context
Protocol, which essentially
allows us to have access to
external tools for our agent.
And if we click on this icon
here, we can see some tools that
are natively installed.
But any additional MCP servers
that we add will also show up
here.
And to add one, all we need to
do is go to our marketplace and
type in at MCP.
And in our case we're going to
want to install the GitHub MCP
server, the official one, which
shows up right over here and I
can install once I've installed
it.
If I now go over to our tools
list, we can see it show up
right over here.
And when we hit the drop down we
see some functionalities that it
provides us.
So why don't we go ahead and
test it out by asking chat to
give me three new feature ideas
for this project and open issues
for them.
And ideally, it could give me
three ideas and use the GitHub
MCP servers to create an issue.
So here are my three ideas.
And right below we could see
where it's going to be using the
GitHub MCP server and I will
give it permission.
Instead of saying allow each
time I'll say always allow.
And this is great.
It looks like it created my
issues here, but I also would
like to show you that I do have
an extension by GitHub that
would allow us to see a variety
of things, such as pull requests
and issues.
And right over here under recent
issues, we could also see it
here.
When I click on it, I have a
nice view of the content within
the issues.
For each of them.
And on top of that, just by
right clicking, I can go ahead
and assign them to our coding
agent at the bottom right hand
corner.
It says issue one has been
assigned to copilot.
So now if we click refresh we
can could see assignees.
Copilot is indicated and I could
do the same for the other two
issues.
And of course, if we come here
on GitHub, we see the same
information is reflected.
And on top of that, if we hop on
over to our agent sessions now
under GitHub Copilot Cloud
Agent, you can see the new tasks
that were assigned.
And just click on any one of
them to spin them up.
Before I wrap up, there's two
cool features that I want to
show you that many don't know
about.
The first is that in this video,
I've been using external
browsers to show the app like
this here, but I do want to let
you know that you are able to
use it within VS Code if you so
choose.
So the next time you're running
an app, if we go to the command
palette and type in simple
browser, you're able to put in
the URL right here.
And then just within VS code you
could navigate through the app.
And this does allow me some
flexibility, such as if I wanted
to go ahead and experiment with
some of the elements here.
I can click start, and it will
allow me to go ahead and
highlight different parts of the
app's elements, such as maybe
right over here.
And once I click on it, it
allows me to have some Dom
information that's attached to
the chat right now, in addition
to a screenshot.
And the other feature that I
want to show you is that when we
choose our models, you see that
we have a large list of
different models, but maybe we
want to see all of these.
We have option right below to
manage our models and that's
including the visibility of it.
So for example currently we see
we have GPT four point one and
four point oh that are on this
list.
If I wanted to just by hovering
over here and double clicking on
the eye here, it will hide this
from the chat model picker and
you can see that there's
slightly greyed out.
So now when we come back, it's
no longer on the list.
The other option that we have
here is to add our own models
from here by using Bring Your
Own key, and here are some
here.by default that could be
added.
And of course you have the
option to just search if you
wanted to just filter it down,
which is all pretty convenient.
Thanks for hanging out with me
in this video.
If you got value out of it, make
sure to hit that like button and
subscribe for more deep dives
like this.
And if you want to keep
learning, make sure that you
also check out this video right
here.
Back To Top

---

*Generated using yt-fetcher CLI*
