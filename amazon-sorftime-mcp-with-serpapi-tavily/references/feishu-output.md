# Feishu Bitable delivery

Feishu delivery is optional. Use it only when the user requests it and provides a target.

## Required inputs

- A full `/base/` or `/wiki/` Bitable URL.
- Prefer a URL containing `table=tbl...` when the base has multiple tables.
- The target base must grant the configured Feishu app edit access.

## Recommended record shape

Map to the target's real columns after inspection; do not assume these names exist:

- Keyword
- Marketplace
- Decision
- Confidence
- Market-capacity conclusion
- Competition conclusion
- Differentiation conclusion
- Google Trends summary
- Main opportunity
- Main risk
- Next action
- Generated date
- HTML report attachment

## Safe sequence

1. Call `feishu_bitable_inspect` with the full link.
2. Match report values to existing column names and types.
3. Stop and report unknown or incompatible columns; never create/rename columns silently.
4. Call `feishu_bitable_append_record` with structured fields.
5. If an attachment-type column exists, pass `report.html` in `attachments` so the same record contains the visual report.
6. Return the record ID and Bitable URL.

The bundled optional connector is under `assets/feishu-mcp/`. It reads `FEISHU_APP_ID` and `FEISHU_APP_SECRET` from its local `.env`; never package the live file.
