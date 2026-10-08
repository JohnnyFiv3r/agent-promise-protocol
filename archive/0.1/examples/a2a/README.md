# A2A 1.0 examples

The Agent Card file is a fragment to merge into a complete native card. The request wraps the existing synthetic buyer intent in A2A `SendMessage`. The extension URI uses example.org for documentation; the release supplies its published URI. These are binding examples, not a running endpoint or completed interoperability test.

The request uses the headers:

```http
Content-Type: application/json
A2A-Version: 1.0
A2A-Extensions: https://example.org/extensions/agent-bazaar/v0.1
```

Authentication uses the endpoint's native declared security scheme. The server must acknowledge extension activation before any dependent Agent Bazaar transition. `ROLE_USER` denotes client-to-server direction, independent of market posture or promise polarity.
