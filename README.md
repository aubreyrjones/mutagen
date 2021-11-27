Mutagen Tabletop RPG Engine
---------------------------

This is the Mutagen Game Engine. It defines basic rules for an
open-source, fiction-first tabletop roleplaying game. It has several
features I consider unique or outstanding:

* Mutagen puts fiction first. Everything in the game is designed to
  help your table tell an exciting and surprising story
  together. "Balance" be damned.

* There's no separate rulebook or character sheet. A "playbook" serves
  as both, providing all the rules and recordkeeping that the person
  using it needs. Each player and the GM gets a playbook with exactly
  what's relevant to their role, and each game has custom playbooks
  containing just what's necessary.

* Made up of modular sections, playbooks are short and
  self-contained. For most games, PC playbooks are 5 pages (6
  max!). The GM playbook might be twice as long. Other than lore,
  nobody needs to read anything else.

* Mutagen is low-stress for players. The rules are brief, and printed
  right on your character sheet for easy reference. Mark Health right
  next to the description of Health.

* Mutagen is fun for GMs. Players owning the narrative means you can
  go with the flow--without risk of drowning. Throw fun problems at
  your PCs without needing to pre-balance everything. Find out what
  happens along with them!


# Playing with Mutagen

* Mutagen uses dice. Random chance helps us tell surprising stories at
  the table. And rolling dice is fun.

* Mutagen is genre-blind and tone-blind, with the core playbooks
  written in universal narrative terms.

* Mutagen may be short, but it's deep. Because it's fiction first,
  Mutagen doesn't fill pages with rules just to have cool stuff. It
  just fills pages with cool stuff. Different playbooks permit wildly
  varied playstyles within the same game, and wide choice in moves and
  their application gives everybody options.

* Mutagen works for campaigns. I've written it tersely as possible to
  get out of the way; but it's designed to support full-length,
  full-engagement campaigns. Bought every ○ in your playbook?  Make up
  some new epic-tier moves.

* Mutagen works for one-shots. Most people can read the rules in
  about 10 minutes if they aren't interrupted, and explore the rest of
  their playbooks in another 10 minutes. So long as the game's premise
  is simple enough, many GMs can get a group playing in half an hour.


# Raw Mutagen

You can run a satisfying game with just the vanilla Meta and Common
Mutagen playbooks, without any additional, specialized playbook
sections. These core playbooks define rules in terms of a few
universal concepts and narrative goals that apply to most RPG
scenarios, not in terms of what a character can specifically do--what
your character wants as opposed to how they get it.

In such a game, each PC mostly has access to the same powers and
resources as the others--however you define that in your world. PCs
can grow and get better at doing stuff with those powers, but they
don't have moves that would let them defy reality differently than
other PCs. Basically, they do whatever people (or whatever) can do in
your world to drive a story forward. If that's driving oxen or a
spaceship, it doesn't matter much for the rules.

You really need specialized moves or playbook sections when different
PCs gain access to significantly different or unique in-game
powers. They define the exceptions to your normal.

# Building with Mutagen

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

FAQ
---

## I thought it was self-contained.

That is not a question, but I take your point. I'm doing my best to
define everything in the core playbooks as clearly as I can. But given
the extreme space constraints, I usually only get 1 shot at defining a
concept. While I've tried to pick framing and style so that most
people understand what I'm writing, I know my description can't work
for everybody. These FAQs are requests I've received for clarification
from some portion of players, but not so many that I want to revise
the rules themselves--or maybe I just haven't thought of a better
solution.

## What's with the dice symbols (⚅⚅, ⚃⚅, etc.)?

These symbols seem to trip up some people, often because they want the
pips displayed in the icon to relate to the physical dice
directly. But the icons are dumber than that: they're just
abbreviations for named results ranges.

* "⚅⚅" is literally just "Critical Success".
* "⚃⚅" is literally just "Full Success".
* "⚂⚃" is literally just "Partial Success".
* "⚀⚀" is literally just "Failure".

Writing out the result range name every time takes too space, and the
name will frequently split over lines making it harder to visually
scan a move's text. The dice are included in most unicode-enabled
fonts, and seem to provide a little bit of mnemonic aid compared to
something arbitrary like ◐ ◑ ◒ ◓. Probably the nearest runner-up was
②, ⑦, ⑩, ⑫: but those symbols aren't the same physical size (which
screws up formatting), feel less "fun" to me than the dice, and suffer
from looking like a specific target number even more than the dice
(imo).

I have a neurological visual problem differentiating visual symbols
(didn't read or write till 3rd grade), so I did my best to make them
identifiable even to my fuzzy brain. If you're having trouble reading
them, it might help to notice that:

  * you don't have to "decode" the symbols by counting the dots. It's
    good enough just to recognize the different shorthands visually.

  * the first die of each icon is unique (6, 4, 3, 1) and visually
    distinct.

  * the dice get visually "less full" as the result range goes down.

  * when written next to each other, results are always listed in
    descending order. So a move will always say "if you roll ⚅⚅ or ⚃⚅"
    and never the other way around.

  


Building Playbooks
------------------

You can manually build full playbooks from their sections using
LibreOffice. But if you're doing it a lot, it's potentially easier to
use the included Makefile.

On Ubuntu, you'll need LibreOffice installed plus `sudo apt install
build-essential poppler-utils`. You can then build the core and
example playbooks with just `make` in the project directory.

You can add your own game to be built by putting it in a `mutation`
subdirectory with a Makefile called `all.mk`. You can define your own
targets in `all.mk` that build your custom playbooks using the pattern
established in the main Makefile.

I haven't tested it on Windows, but you should be able to edit the top
of the Makefile to point at your `soffice.exe` executable and whatever
command line tool you're using to concatenate PDF documents. I don't
know what tool concatenates PDF on Windows--I only play videogames on
Windows.

It's pretty easy to figure out the build if you know `make` a little
bit and read the comments, and it's probably impossible to figure out
if you don't know `make`. Teaching `make` is beyond the scope of this
text. If it looks like gibberish to you, ask your techy friends if
they know somebody.


# Copyright and License

Copyright 2021 by Aubrey R. Jones.

The work contained in this repository is licensed under the Creative
Commons Attribution-ShareAlike 4.0 International License. To view a
copy of this license, visit
http://creativecommons.org/licenses/by-sa/4.0/ or send a letter to
Creative Commons, PO Box 1866, Mountain View, CA 94042, USA.


## CC Share Alike? I thought you said commercial was cool!

Okay, stay with me for a minute. I've been hacking away at this engine
for, like, a lot of hours now. I've got all the general rules to tell
an exciting adventure story cut down to 4 pages that work unchanged
for (most) any world. Even if you knew you'd license an engine, did
you expect to get it down to 4 pre-written pages?

What's more, you don't even have to print those pages in your
book. You're gonna publish them in PDFs just like you'd planned for
your character sheets. Character sheets you're not gonna have to
design anymore--although of course you can tart them up if you've got
the budget. You also get free modular document generation if you can
find (or are) the right kind of nerd to run `make`.

Unless you want to, you don't have to publish any mechanical rules in
your book. You can fill every page with the awesome fruits of your
imagination without wasting anything on how tables play out the next
narrative beat. Or you can cut your page count and widen your margin.

If you don't screw it up, you're going to write maybe 1 page (2 pages
max!) for the playbook representing each class or whatever in your
game. And since there's literally no space for lore or worldbuilding
in those measley columns, they're gonna be almost 100% game
mechanics.

Finally you've got to remember: this is a fiction first game, so the
'game mechanics' just call right back into the fiction anyway. That'd
be the book you're selling. [Or actually it could be a movie, a novel,
Patreon serial, or any other media you're making. I'd love to see some
author publish playbooks to go with their novel.]

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
free game engine you don't even have to print--you can't even share
*that much*?



