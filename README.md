Mutagen Tabletop RPG Engine
---------------------------

This is the project page for the Mutagen Tabletop Game Engine. If
you're a player or a GM, you probably want [the Mutagen
website](https://www.mutagenrpg.com). This page is primarily meant for
homebrewers and designers.

Mutagen is a little different from other tabletop engines you might
have met. It's a whole ecosystem. There are three main parts:

  * The flexible, extensible, fiction-first core rules.
  * The document generation system contained in this project.
  * The `mutagenrpg.com` website, which provides a web-app for live
  character sheets.

Design philosophy for the rules themselves are in files under the
`designer` directory.

The document generation system is described below. It creates PDF
playbooks for printing and electronic playbooks for use on the
website.

The `mutagenrpg.com` website lets players upload the electronic
playbooks created by the document generation system, edit write-in
fields, toggle purchased powers, etc. 


# Building with Mutagen

Mutagen is designed from the ground up to support modular additions in
the form of new moves and playbook sections. Because the flexible
_story moves_ system resolves risk and conflict in the story, you
don't need to include those kinds of considerations when designing a
move. A move can be as simple as "○ Speak to Animals - You can speak
to and understand animals."

You can add moves piecemeal as much as you want (that's how I built
and refined Mutagen), but you might want to make a whole game world's
worth of moves and playbook sections, presented coherently like the
example playbooks. I call this a "mutation". A mutation is
self-contained and suitable for distribution directly to your players.

In addition to everything above, here's why you might want to build
your game or homebrew with Mutagen:

* The Mutagen core (4 pages total for the Meta and Common playbooks)
  is ready to go to out of the box to handle anything "normal"--no
  matter what normal means in your world.

* Layer in character progression, specialization, and differentiation
  through new playbook sections without rewriting anything. Easily
  represent playable "classes", tropes and archetypes, or even unique
  iconic characters.

* Homebrew is first class. You can play Raw Mutagen plus a few custom
  moves you make up and jot on notepaper before or during the game
  sessions. Formalize things into playbooks when you're ready; or
  don't.

* There's meta-meta support. :) There's a Designer playbook which
  might help you get into the Mutagen headspace when writing a game or
  homebrew using the system. There's also a simple automation
  framework for piecing together multiple playbooks into seamless
  final documents for your players.

* It's open source, even for commercial use. The core Mutagen system
  and several example playbooks are available for your own use,
  without asking permission, even for commercial purposes--with
  certain restrictions. You can protect your lore, world, art, merch
  and stuff under regular trade law. See "Copyright and License" below
  for more.



# Document Generation

You write Mutagen playbooks using Mutagen Markup. You'll edit most of
the playbook files with a basic text editor, Notepad even, not a word
processor. The Markup is then automatically turned into ODT, PDF, and
electronic playbook files.

You can write separate playbook sections as separate files, and you
can combine them as you like. The whole thing is turned into a single
playbook by the automatic system.

The system is tested constantly on Ubuntu Linux and regularly on
Windows 10 Home. I expect the Linux instructions can be used with only
a little modification on Mac, but a tale old as time: I don't have one
and haven't tested it.


### Linux Prereqs:

1. Make sure you have `python3` installed. This is included on most
   modern distros.

2. Do `pip3 install pypdf2`.

3. Install LibreOffice 6.0 or higher.


### Windows Preqs:

1. Download Python 3.9 or higher from the official website
   (https://www.python.org/downloads/windows/). Use the version that
   says "Download Windows installer" (_not_ "embeddable package").

2. IMPORTANT! Check the box that says "Add Python 3 to PATH".
   ![Add to path in installer](./_images/add_to_path.png)

3. IMPORTANT! On the last step of the installer, click the option that
   says "Disable path length limit".
   ![Disable restrictions in installer](./_images/extend_path.png)

4. Double-click `SETUP.py`. This will download some requirements and
   tell you if they were successfully installed. If it doesn't work,
   it's typically because of a mistake in one of the steps above, or
   because of something like anti-virus or other intrusive software.

5. Install LibreOffice 7.0 or higher.
   (https://www.libreoffice.org/download/download/)

   IMPORTANT! Install LibreOffice in the default location on your computer.


### Playbook Definitions

Playbooks are made up of multiple sections, each as a separate text
document. The playbook definition file tells the script which sections
go together into which playbooks. Look at the included `playbooks.txt`
for an example.

Each line of the file consists of a final playbook filename, then an
equal sign, then a list of each playbook section in the order they go
into that playbook. The Mutagen Meta section is _automatically_
appended to the end of every playbook created.

Do NOT! include the extension (`.txt` or `.pdf`) on any of these
file names. All of that is handled automatically.

```
output_name = common/first_section your_game/second_section your_game/third_section
```

You can edit the included `playbooks.txt` or make a new one for your
game.


x### Running the Build

Once you've gotten the prereqs out of the way, you should be able to
run the build.

If your playbook definitions are in `playbooks.txt`, you can just:

Linux: Run `./compile_playbooks.py` from the command line.

Windows: Double-click `compile_playbooks.py`.


If you want to use a different playbook definition file, you'll have
to use the command line on both systems:

Linux: `./compile_playbooks.py my_playbooks.txt`

Windows: `python compile_playbooks.py my_playbooks.txt`


This will create a bunch of intermediary files in the `build`
directory. You can ignore these.

The complete PDF playbooks are created in `playbook_output`, with the
electronic tracker teplates in a subdirectory.

## Mutagen Markup

Mutagen Markup is made from several uncommon unicode symbols. There's
a reference in `unicode_symbols.txt`. As you write Mutagen playbooks,
you can just copy and paste the symbols from there--that's what I
do. It's a little weird at first, but it becomes a really tight
shorthand pretty quickly.

Line breaks and formatting are fairly important. Special line types
like roll results, write-in fields, or list items won't work if you
don't start them on a new line. Hit enter _twice_ to start a new
regular-text paragraph.

There are two basic blocks of text you can format:

  * sections
  * moves

Sections start with `§`. Optionally, you can write `~~~§`, which will
force a (print) column-break before that section. You can also write a
(single) paragraph of text underneath the section to describe it.

Moves start with a line containing `►`. Do not use that symbol
anywhere else or for any other purpose.

Look at `common/common.txt` under Common Aptitudes for examples of
various special formats. Also check out `pcs/wizard.txt` under
Concentration for labeled inputs examples.


### Tracker Template Extraction

The playbook builder script also extracts a computer-readable listing
of all moves for each playbook. Each playbook's moves are stored in a
separate file with a `.mutagen.json` extension. These files are
intended for use in the (upcoming) digital playbook webapp.

In order for this feature to work correctly, there are some technical
requirements.

1. Use _exactly_ the same symbols as the core sections. You should
   _copy and paste_ the symbols--don't try to do it by sight, because
   many symbols look similar or identical but have different computer
   representations. For your convenience, there is a file
   `unicode_symbols` that has all of the weird symbols used in the
   playbooks.

2. Define every one of your items or moves with `►` after the name. Do
   _not_ use that symbol for any other purpose or in any other place.

3. Include the `§` at the beginning of every section name. If you
   don't, the last move before the section name will eat up and
   include the section name and any flavor text after it.

4. Use exactly the included `○△●▢` symbols for buyable and trackable
   items. These are the only "clickable" symbols in the app.

5. Use the same format for aptitudes as in the core sections, with the
   `○` on either side of the aptitude name and the `►` after the last
   `○`: `○ APT_NAME ○ ○ ○ ►`. The number of `○` isn't important.

6. Avoid complex formatting in move text. Keep it simple.

7. For text inputs (places where players are expected to put notes),
   carefully follow the format shown in the Common Name/Concept/Drives
   and Example Wizard Concentration items. Use the two-line example
   for items where the player only needs to write a couple words. Use
   4+ lines for a sentence.

   Labeled inputs (like Drives or Concentration) must follow the exact
   3-line formula. Horizontal spacing is not important, but the lines
   are.  The first line has the bracket-top characters; the second line
   has the label; the third line has the bracket-bottom characters.


Copyright and License
---------------------

Copyright 2021 by Aubrey R. Jones.

The work contained in this repository is licensed under the Creative
Commons Attribution-ShareAlike 4.0 International License. To view a
copy of this license, visit
http://creativecommons.org/licenses/by-sa/4.0/ or send a letter to
Creative Commons, PO Box 1866, Mountain View, CA 94042, USA.


### CC Share Alike? I thought you said commercial was cool!

Okay, stay with me for a minute. I've been hacking away at this engine
for, like, a lot of hours now. I've got all the general rules to tell
an exciting adventure story cut down to 4 pages that work unchanged
for (most) any world. Even if you knew you'd license an engine, did
you expect to get it down to 4 pre-written pages?

What's more, you don't even have to print those pages in your
book. You're gonna publish them in PDFs just like you'd planned for
your character sheets. Character sheets you're not gonna have to
design anymore--although of course you can tart them up if you've got
the budget. You also get free modular document generation and
automatic, seamless, free integration into the Mutagen Character
Tracker app.

Unless you want to, you don't have to publish any mechanical rules in
your book. You can fill every page with the awesome fruits of your
imagination without wasting anything on how tables play out the next
narrative beat. Or you can cut your page count and widen your margin.

If you don't screw it up, you're going to write 1-2 pages for the
playbook representing each class or whatever in your game. And since
there's literally no space for lore or worldbuilding in those measley
columns, they're gonna be almost 100% game mechanics.

Finally you've got to remember: this is a fiction first game, so the
'game mechanics' just call right back into the fiction anyway. That'd
be the book you're selling. [Or actually it could be a movie, a novel,
Patreon serial, or any other media you're making. I'd love to see some
author publish playbooks to go with their novel--DM me, I'll help.]

So check it out: in your book, which you're publishing for cash moneys
and claim trad copyright on, you describe this dope-ass creature you're
calling a Mana Guppy. You tell your readers all about the crazy shit
it can do, how it looks, what it expects from its chosen Guppy
Tender. That's all in your book with trad copyright. Within the law,
ain't nobody gonna yoink your Mana Guppy.

Then in a completely separate PDF you were gonna give away anyway,
you'll put a line in the Guppy Tender playbook that's like `○ Summon
Mana Guppy - Spend 1 Guppy Bait. If the conditions are right, you
summon your Mana Guppy.` And you're telling me--the guy giving you a
free game engine you don't pay to print--that you can't even share
*that much*?

FAQ
---

### I thought it was self-contained.

That is not a question, but I take the rhetorical point. I'm doing my
best to define everything in the core playbooks as clearly as I
can. But given the extreme space constraints, I usually only get 1
shot at defining a concept. While I've tried to pick framing and style
so that most people understand what I'm writing, I know my description
can't work for everybody. These FAQs are requests I've received for
clarification from some portion of players, but not so many that I
want to revise the rules themselves--or maybe I just haven't thought
of a better solution.

### No questions?

I just eliminated the only major confusion feedback I've gotten. Go
back in the repo to see what I'm talking about if you care enough. I'm
sure there'll be more later.


# Acknowledgements and Thanks

Games that inspired Mutagen: _Blades in the Dark_, _Scum & Villany_,
_Apocalypse World_, _GURPS_, _Vampire: the Masquerade_.


Thanks to:

* K for endless test reading.

* L for endless enthusiasm and encouragement.

* My online table: H, L, and K for being my first guinea pigs.

* My kitchen table: E, Z, K, and B 'cause they didn't sign up for this
  shit.

