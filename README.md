# Dive to the Heart

A 100% completion tracker for **Kingdom Hearts HD 1.5 + 2.5 ReMIX** — every chest,
trinity, recipe, superboss and trophy across all four journeys (2,546 objectives).

Implementation of the `Dive to the Heart - KH Tracker.dc.html` design from the
*Kingdom Hearts Completion Tracker* Claude Design project.

## Running it

Open `index.html`. That's it — it is self-contained (no build step, no server, no
dependencies), so double-clicking the file works. Serving it over http also works:

```bash
python3 -m http.server 4173 --directory .
```

## Saving progress

Progress lives in your browser's `localStorage`, key `kh-dive-tracker-v1`:

```json
{ "v": 2, "m": 1, "checked": { "kh1-chest-tt-04": true, "bbs-sticker-t-07": true } }
```

Only the ids you've ticked are stored. Two smaller keys sit alongside it: `kh-dive-prefs`
(sound on/off and volume) and `kh-dive-sfx` (any custom sound files you've loaded). Neither
is touched by Export/Import, which carry progress only. Writes are debounced 250 ms after your last
click, with a flush on page close. Nothing leaves the machine — no account, no server,
no network call involved in saving.

**localStorage is per origin.** A double-clicked `file://` copy and a page served from
`http://localhost:4173` keep *separate* progress, and moving the file can orphan it.
So pick one way to open the tracker and stick to it. **Export save** writes a JSON file
you can **Import** anywhere, which is the way to move between origins, browsers or machines.

### Carrying over the original tracker

On first run the app reads the old tracker's key (`kh-15-25-100-tracker-v1`) and adopts
its progress, reporting *"Carried over N checks from your old tracker"* under the title.
That only works when both pages are opened from the **same origin** — the old tracker was
a file you double-clicked, so open this one the same way to get it automatically.

If it doesn't fire, the old save is already in the right shape to import. Open the old
tracker, and in the browser console run:

```js
(() => { const a = document.createElement('a'); a.href = URL.createObjectURL(new Blob([localStorage.getItem('kh-15-25-100-tracker-v1')], {type:'application/json'})); a.download = 'kh-old-save.json'; a.click(); })()
```

Then hit **Import** here and pick that file.

## Views

- **Stations** — overall dive percentage, one stained-glass ring per game, and 16 insignias.
  Percentages cover in-game completion only; PlayStation trophies are tallied separately.
- **Checklist** — objectives with search, *Hide completed*, *Missable only*, expand/collapse,
  and the timing controls below.
- **Worlds** — per-world completion, derived from the chest groups; *Open in checklist*
  focuses the checklist on that world.
- **Story (Birth by Sleep only)** — Terra / Ventus / Aqua. BbS is three separate playthroughs
  and all three are needed for 100%, so the checklist and Worlds scope to one character's
  journey. See below.
- **Road to Platinum** — trophies by phase, tallied by Bronze/Silver/Gold/Platinum.
- **Synthesis planner** — rolls every unchecked recipe into a single farm list of
  materials still needed, each with the enemies that drop it, their rate and where they live.
  Checking a recipe off drops it out of the list.
- **Enemies** — the enemy manifest: portrait, the worlds it appears in, and what it drops.
  Search matches enemy names, worlds *and* drop items, so typing `power shard` returns
  everything that drops one.
- **Sources** — the wikis and guides each game's data came from.

## Timing — when you can (or should) get things

Every group in `kh-data.json` carries a `when` bucket, and individual items can override
their group. The checklist exposes this two ways:

- **Group: Category | When** — *Category* is the collectible-type view; *When* regroups the
  same objectives into timing bands, in the order you meet them on a route. Switching to
  *When* auto-opens the three bands you can permanently lose.
- **Timing chips** — filter to a single band in either grouping, with a live `done/total`
  per band. Bands with anything still at risk are outlined in amber.

| Bucket | Band | Meaning |
| --- | --- | --- |
| `plan` | Plan before you start | Locked in at file creation — a run that breaks one can't be fixed later (difficulty, no-continue, no-equipment-change). |
| `prologue` | Prologue only ⚠ | Permanently lost the moment the prologue ends. |
| `window` | Limited story window ⚠ | Lost if you push past the story beat named in the entry. |
| `story` | As you play through | Picked up on the normal path, first time you're there. |
| `revisit` | Needs a return trip | Gated behind growth abilities, a later Trinity, or a second visit. |
| `endgame` | Before the finale | Late sweep, while everything is still open. |
| `postgame` | After the credits | Only reachable once the story is cleared. |
| `anytime` | Anytime / ongoing | Farming, shops, melds, repeatables. |

Assignment is at **group** granularity, with item-level overrides where an entry's own note
contradicts its group — e.g. the four KH1 chests behind a limited story window sit in
`window` even though their world group is `story`, and Ansem's Reports 11–13 move to
`endgame` because they drop from the Final Mix superbosses. Buckets are grounded in each
category's own note text (which states what is and isn't missable) and in the story order
the chest groups are already listed in. A game only shows the bands it actually has —
KH1 has no `postgame` band, because all five of its superbosses stay available right up
until you finish the game.

## Trophies are counted separately

PlayStation trophies do not count toward the completion percentage. They have their own
tally, shown next to the objective count on the Stations hero, on each station tile, and as
a chip in the game header:

| | Objectives | PS trophies |
| --- | --- | --- |
| KH Final Mix | 487 | 56 |
| Re:Chain of Memories | 328 | 48 |
| KH II Final Mix | 678 | 51 |
| Birth by Sleep | 852 | 46 |
| **Total** | **2,345** | **201** |

Birth by Sleep's trophy category holds 54 entries, but only 46 are PlayStation trophies —
the other 8 are the **in-game Trinity Archives trophies**, which are game completion rather
than PSN, so they stay in the objective count. That is why BbS still shows a small
`Trophies 0 / 8` section when trophies are hidden. Groups carrying PlayStation trophies are
marked `ps: true` in `kh-data.json`.

**🏆 Trophies shown / hidden** in the checklist filter bar takes them out of the way
entirely, and the preference persists in `kh-dive-prefs`. Hiding them is thorough — they
also drop out of the Worlds rows, the station tiles' category lists, the timing and story
chip counts, the "categories complete" chip, the missable warnings, and *What next*. For KH1
that means the "Plan first" band disappears and the missable count goes to zero, because all
three of its missables are the plan-from-the-start trophies. **Road to Platinum** is
unaffected — it stays available as the trophy view.

## Enemy manifest

`kh-enemies.json` — 259 entries across the four games, scraped from khwiki's enemy infoboxes
rather than written by hand:

| Game | Enemies | With drop tables | With worlds | With art |
| --- | --- | --- | --- | --- |
| KH Final Mix | 71 | 47 | 64 | 71 |
| Re:Chain of Memories | 38 | — | 36 | 37 |
| KH II Final Mix | 93 | 73 | 91 | 87 |
| Birth by Sleep | 57 | — | 49 | 57 |

Rates come from the **Final Mix** fields (`FMreward`, `FM2reward`), falling back to the
vanilla ones, so they match the versions this tracker covers. Worlds come from `KHworld` /
`KH2world`, and BbS from the per-character `BBSworldT/V/A` — which means BbS enemies also
carry `chars` and respect the Story filter.

Re:CoM and BbS show no drop percentages because those games have no percentage drop tables;
their enemies give cards and prize-pod commands instead. Their manifest entries are still
worth having for *where each enemy appears*, and the view says so rather than looking broken.

Every portrait was verified to exist by loading it — not guessed from a filename pattern.
Two traps if you regenerate: a naive `KHII` match also matches `KHIII`, and enemy pages
embed unrelated screenshots, so only files actually **named after the enemy** are considered.

Where an enemy drops the same item at several rates (the Final Mix variant tables — a
Powerwild slipping on a banana peel, say) the manifest keeps every rate, and the raw drop
line is shown underneath for context. The farm list instead shows one row per enemy at its
best rate, so four rows means four different enemies to hunt.

Regenerating: edit `kh-enemies.json` and run `python3 sync-data.py`, which re-embeds it and
`kh-data.json` into `index.html`.

## Birth by Sleep — three stories

BbS is three playthroughs, and every objective in `kh-data.json` carries the characters it
belongs to: `chars: ["T"]`, `["A","V"]`, `["A","T","V"]`, or nothing at all. **Story** chips
above the checklist scope everything to one character.

723 of 898 objectives are tagged. Chests are fully tagged and the per-character totals come
out at **Terra 122 · Ventus 130 · Aqua 130** (122 + the 8 Aqua-only Secret Episode chests),
matching the counts the category's own note states. The 175 untagged objectives — trophies,
the Xehanort Reports, the superbosses — are genuinely shared, so they appear in all three
stories.

Tags are derived from the data itself: a `Characters: T/V/A` prefix on the item note, else
the character named in the group (`Dwarf Woodlands — Ventus`, `Terra's Stickers`), else
"Aqua only" text, else shared.

**One limitation worth knowing.** Roughly 300 objectives across Commands, Melding, Shotlocks
and Minigames are tagged `T/V/A` and have a *single* checkbox between them, because that is
how the data is shaped. In the game each character fills their own Report, so strictly these
want three ticks each, not one. Splitting them would triple those entries and change their
ids, which would orphan any progress already saved against them — so it is not done. Chests
and stickers, which are the bulk of the per-character work, are unaffected.

## Display flags

Appended to the URL (the design exposed these as canvas controls):

| Flag | Values | Default |
| --- | --- | --- |
| `motion` | `full`, `calm`, `off` | `full` (`off` when the OS asks for reduced motion) |
| `art` | `on`, `off` | `on` |
| `density` | `comfortable`, `compact` | `comfortable` — `compact` hides category notes |

e.g. `index.html?motion=calm&density=compact`

## Sound

Interface feedback is synthesised with the Web Audio API — no audio files ship with the
tracker. Seven voices, written to sit in the same register as a KH menu (short crystalline
bells, fast attack, exponential tail):

| Voice | Fires on | Character |
| --- | --- | --- |
| `move` | any button, tab or accordion | 28 ms cursor tick, ~4 kHz |
| `select` | export, unmute | bright confirm |
| `check` | an objective goes down | 180 ms bell + two sparkle blips |
| `uncheck` | an objective comes back up | shorter, descending |
| `cancel` | reset, failed import | low descending pair |
| `chime` | a group cleared | three ascending bells |
| `fanfare` | a category or a whole game | four bells + sparkle |

Duration and pitch escalate with significance; negative actions descend. Peaks sit around
-13 dBFS with no clipping. The audio context is created lazily inside the first click that
needs it, so nothing plays on load and the autoplay policy is satisfied.

**♪ Sound** mutes; the preference persists in `kh-dive-prefs`. From the console:
`khSfx.vol = 0.3`, `khSfx.play('fanfare')`, `khSfx.clearCustom()`.

### The game's own sounds

`sounds/` holds seven sounds cut from the extracted `se000` system bank in
`System Sound Effects/` — trimmed of leading silence (every file had ~23 ms of it, which
you feel as lag on a UI blip), faded at both ends so the trim can't click, and normalised
to -1 dBFS. 205 KB total. These override the synth wherever they load.

Nothing about Square Enix's audio ships in this repo's code — `sounds/` is cut from **your**
extraction of **your** copy. If you pass this tracker to anyone else, delete `sounds/` and
`System Sound Effects/` first; the synth voices take over on their own.

**The bindings are a guess.** They were chosen from waveform shape alone — attack time,
duration, and whether the pitch rises or falls across the sound — because nothing in the
bank is named. Open **`sfx-audition.html`** to fix any that are wrong: it loads all 179,
draws each waveform, plays them on click, and binds them to roles. **Apply to tracker**
saves your choices into `kh-dive-sfx` (they beat both the synth and `sounds/`), or copy the
`cp` commands it prints to make them permanent in `sounds/`.

| Voice | Bound to | Why |
| --- | --- | --- |
| `move` | `#19` | 69 ms, 0.4 ms attack, rising 4.5k→7.7k — sharpest tick in the bank |
| `select` | `#10` | 192 ms, rising 1.6k→3.7k |
| `check` | `#1` | 95 ms, peak .72, rising 4.3k→5.4k — reads as the confirm bell |
| `uncheck` | `#177` | 112 ms, falling 6.1k→2.5k |
| `cancel` | `#7` | 138 ms, two onsets, falling 5.3k→2.0k |
| `chime` | `#26` | 417 ms, four onsets, rising 5.0k→8.3k |
| `fanfare` | `#21` | 989 ms, three onsets, peak .76, rising 4.8k→8.7k |

Loading order, highest priority first: your saved bindings (`kh-dive-sfx`) → the `sounds/`
folder → the synth. Over http the folder is fetched and decoded into Web Audio; from
`file://`, where `fetch` is blocked, it falls back to plain `<audio>` elements, which can
read neighbouring files. **Load SFX** in the header also takes files directly from a picker,
which works from `file://` too — name each file after the voice it replaces (a name merely
*containing* it works, so `kh2_check.wav` matches `check`).

For reference, the extraction route: [OpenKH](https://openkh.dev) unpacks the `.pkg`/`.hed`
archives, and the `.scd` sound containers inside convert to wav with
[vgmstream](https://vgmstream.org).

## Art

Every icon resolves through **khwiki**'s `Special:FilePath`, which redirects to the current
file and returns a real 404 when a file is gone. The Kingdom Hearts **Fandom** mirror is
deliberately not used: its `Special:FilePath` answers missing files with a 300x171 "no
image" placeholder instead of a 404, so a dead link there *loads successfully* and renders
as a silent grey box. Every art name in the app and every group thumbnail in the data was
checked against khwiki's own file list.

Each station tile carries the box art for the exact edition in HD 1.5 + 2.5 ReMIX — the JP
Final Mix cases for KH, KHII and BbS, and the NA Re:Chain of Memories case — pulled from
khwiki like the rest of the art.

The **Dive to the Heart** world image is the one piece of art stored locally rather than
linked: the original is in `art/`, and a 512px copy is embedded in `kh-data.json` as a data
URI (85 KB) so it survives being opened any way at all. If you swap it, note that `cssUrl()`
must not escape the comma in `data:image/jpeg;base64,` — commas are legal unquoted in CSS,
and escaping that one silently breaks the image.

The progress rings are **not** an image — each is an inline SVG rose window generated in
`ringFace()`: a rim band of alternating panes, twelve ogee arch panes with lit glass cores,
six portrait medallions, and a calm centre so the percentage stays readable on top of it.
The face doesn't depend on progress (that's the two `conic-gradient` layers painted over it),
so one SVG per palette is built once and cached — five in total, regardless of how many rings
are on screen.

Two encoding traps if you edit it: `encodeURIComponent` leaves `(` and `)` raw, which would
end an unquoted CSS `url()` early, so they're escaped explicitly; and the SVG needs explicit
`width`/`height` (not just a `viewBox`), because `background-size` in a multi-layer `background`
shorthand applies per layer and an intrinsically-sized-less SVG lands at 150x150.

KH1-only synthesis materials (Spirit/Blaze/Thunder shards, Gale, Mystery Goo, ...) have no
icon on either wiki and fall back to a same-tier stand-in, so the farm list never shows a hole.

## Files

| File | Purpose |
| --- | --- |
| `index.html` | The whole app — markup, styles, logic, and the embedded objective data. |
| `kh-data.json` | Canonical objective data. The source of truth for edits. |
| `kh-enemies.json` | Enemy manifest — portraits, worlds and drop tables. |
| `sync-data.py` | Re-embeds `kh-data.json` and `kh-enemies.json` into `index.html`. |
| `sfx-audition.html` | Audition the extracted sound bank and bind sounds to interface voices. |
| `sounds/` | The seven bound interface sounds (205 KB). |
| `art/` | The Dive to the Heart station artwork (the source for the embedded copy). |
| `System Sound Effects/` | Your raw `se000` extraction, 179 files. Only `sfx-audition.html` reads it — safe to move elsewhere once you're happy with the bindings. |

Editing objectives:

```bash
python3 sync-data.py
```

`index.html` prefers its embedded copy of the data and falls back to fetching
`kh-data.json` only if the embedded block is missing (which needs a server).

## Data shape

```jsonc
[{
  "game": "kh1",                       // kh1 | recom | kh2 | bbs
  "title": "Kingdom Hearts Final Mix",
  "sources": [{ "title": "...", "url": "..." }],
  "categories": [{
    "id": "chests",                    // drives the category icon and the Worlds/Synthesis/Trophy views
    "name": "Treasure Chests & Item Pickups",
    "note": "shown above the group list",
    "groups": [{
      "name": "Traverse Town",
      "img": "https://kh.wiki.gallery/images/...",   // optional thumbnail
      "link": "https://...",                          // optional map/wiki link
      "when": "story",                                // timing band for this group (see above)
      "items": [{
        "id": "kh1-chest-tt-01",       // stable — this is what gets saved as checked
        "name": "Potion",
        "location": "1st District — ...",
        "note": "optional caveat",
        "missable": false,
        "when": "window"               // optional — overrides the group's band for this item
      }]
    }]
  }]
}]
```

Category ids with special behaviour: `chests` seeds the **Worlds** view,
`synthesis` seeds the **Synthesis planner** (its `Materials…` group supplies drop
sources, and recipe locations are parsed for `Materials: Name xN`), and `trophies`
seeds **Road to Platinum** (tier is read from `(Bronze)`/`(Silver)`/`(Gold)`/`(Platinum)`
in the trophy name).
# KHWalkthrough
