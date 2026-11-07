# User Only
This is a ad-hoc scribble pad for me, the user, to use.  No need to read further.

## Should this kind of usage convo be avoided?
Keep the edits surgical. Multiple edit calls on the same file — must they be sequential? They’re independent text regions; can I batch them in one message (multiple edits to the same file — order of application? They’re independent, non-overlapping regions; parallel edits to the same file risk conflicts. Safer: sequential, or one big edit? Multiple distinct small edits; do them one per message? That’s too many round trips. The edit tool applies immediately; parallel calls to the same file — the tool probably serializes, but each edit matches oldString independently; regions don’t overlap so order doesn’t matter. Batch 4 edits in one block.
