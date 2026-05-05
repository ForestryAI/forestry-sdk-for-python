# Forestry AI Chat module
The Forestry AI Chat module is semantic augmentation against trained vectors extracted from Microsoft Teams.  Forestry uses group channels in Teams for informal education.

## Goal
The semantic augmentation of chats aims to incorporate facts from an unofficial source into generalized models based on official documentation.  The difficult part is calculating the degree of truth.  The inclusion of facts from Microsoft Teams will likely need human help.

## Design
This module performs stages to find facts and enrich them with metadata.  It extracts primarily adjacency pairs (e.g. questions with answers) and secondarily statements.  Microsoft Teams has a Microsoft Graph [API](https://learn.microsoft.com/en-us/graph/api/resources/teams-api-overview?view=graph-rest-1.0) interface to pull chats from group channels.  Private chats are excluded.

### Adjacency pairs
An adjacency pair from chats has specific characteristics beyond general linguistic or philosophical definitions.  These dimensions (e.g. metadata) shape how a question is interpreted, surface and acted upon inside Microsoft Teams.

#### Intent
Intent is why the question was raised in Teams and not an abstract inquiry.  Here is a list of **common** intents:

- Information seeking - "What is a collective price listing?"
- Decision enabling - "Should we release with this bug fix?"
- Action triggering - "Can you review my answer to the customer?"
- Confirmation or validation - "Is this what she/he meant?"
- Problem solving - "Why can destination failing validation?"

What we see with the above questions is that they often expect **action**.

#### Audience
A group channel has members that comprise an **audience**.

- Individual direction - tagging users
- Role based - "Can the third-line verify this?"
- Group wide - "Does anybody know when a bug fix is coming?"
- Implicit ownership - certain groups assume a responsibility eg. access control

The same question phrasing means different thing depending on where it is posted.

#### Urgency
Time pressure is often implicit rather than explicit.

- Blocking - "Can this case be closed?"
- Near - "Can somebody answer the customer?"
- Low urgency - "When you get a chance..."

In Teams, urgency affects notification behavior, escalation and expectations of response time.

#### Context
Questions are rarely standalone.

- Thread - relies on prior messages
- Linked - tied to a document, PR, meeting notes
- State - relevant only at a specific release phase

The meaning often breaks if the question is copied outside the channel.

#### Persistence
Teams questions exist in a semi-permanent knowledge space.

- Ephemeral - relevant only in the moment.
- Searchable - future group members may find it.
- Durable - answers act as informal documentation

This affects how carefully questions (and answers) are phrased.

#### Social dynamics
Internal hierarchies influence how a question is constructed.

- Upward - often softened or indirect
- Peer - more casual, shorthand-heavy
- Downward - can double as instructions

Grammar is often altered for politeness and risk, not clarity alone.

#### Platform
Non-linguistic dimensions:

- Mentions - "at-sign" assign responsibility
- Reactions - "thumb up" is a partial or implicit answer
- Threading - singular adjacency pair
- Edits - refine or edit questions post hoc

So questions can be answered without text.

#### Lifecycle
There is usually a lifecycle to chats:

1. Asked
2. Clarified
3. Answered
4. Acknowledged
5. Archived / forgotten / reused

When a step is not down it can signal blocking or breakdowns in ownership.

### Statements
A statement is much clearer or shorter but shares many dimensions of an adjacency pair.

## Stages
TODO: What augmentation functions + profile to use from Forestry AI Core