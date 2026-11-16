# AI Lab · Vibe Analytics, Vibe Coding And MCP

**FH OÖ · Sina Mirshahi · 20 November 2026**

Course material for one session. One case runs through the whole session: an invented company in Upper Austria sells spare parts and must sign new contracts with its carriers (delivery companies). The head of logistics asks: **For each country, which delivery company (carrier) should we use? And when is the faster, more expensive Express service worth its price?**

You answer in three steps. First, an AI writes the code for your analysis (vibe analytics). Then an AI builds an app from your answer, without you writing the code (vibe coding). Finally, you give an AI tools, so that it can find information on its own (MCP, the Model Context Protocol). Every step ends with a check that you can trust.

## Start here

You need two things: a **Google account**, and one **AI assistant** that you can use (ChatGPT, Gemini, Claude or Copilot).

1. Open notebook 1: click its **Open in Colab** button in the table below.
2. Follow the notebook from the top. It tells you each step.

**The plan:** block 1 is notebook 1 and section 1 of notebook 2. Block 2 is the rest of notebook 2, then notebook 3. At the end you post three lines in the chat, or give them to me on paper: one carrier recommendation with its number, one app check you ran, and one thing you learned from a recording.

Share only course data with AI tools, never company data.

## Notebooks

| Notebook | What you do | Open in Colab |
|---|---|---|
| [1 · Ask Your Data](notebooks/1_ask_your_data.ipynb) | Block 1: ask an AI about the export, check the data, agree on a definition, compare within each country | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/FH-Prevail/ailab/blob/main/notebooks/1_ask_your_data.ipynb) |
| [2 · Build The App](notebooks/2_build_the_app.ipynb) | Section 1 in block 1 (read the spec). The rest in block 2: let an AI write the app, run it in your browser, test it with numbers you know | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/FH-Prevail/ailab/blob/main/notebooks/2_build_the_app.ipynb) |
| [3 · Give The AI Tools](notebooks/3_give_the_ai_tools.ipynb) | Block 2: an MCP server with four tools, recordings to check, and (optional) your own questions to Gemini | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/FH-Prevail/ailab/blob/main/notebooks/3_give_the_ai_tools.ipynb) |

If a button does not open, copy the address: https://colab.research.google.com/github/FH-Prevail/ailab/blob/main/notebooks/1_ask_your_data.ipynb, https://colab.research.google.com/github/FH-Prevail/ailab/blob/main/notebooks/2_build_the_app.ipynb, https://colab.research.google.com/github/FH-Prevail/ailab/blob/main/notebooks/3_give_the_ai_tools.ipynb. Or open Colab, choose **File, Open notebook, GitHub**, and type `FH-Prevail/ailab`.

## Words we use

| Word | Meaning |
|---|---|
| **carrier** | A delivery company that transports our shipments. |
| **Standard**, **Express** | Normal and fast delivery; Express costs more. |
| **on time** | Delivered on or before the promised day. |
| **known result** | We know if the shipment was on time or late (a lost shipment counts as late). |
| **not known yet** | The shipment was still on its way when the export ran (end of 31 December 2025), and its promised day was later. |
| **metric contract** | Our written rules for counting, so that everybody gets the same number. |
| **prompt** | The text that you send to an AI: your question or your instructions. |
| **vibe analytics** | You ask an AI in plain words to analyse data, and you run and check the code it writes. |
| **vibe coding** | You ask an AI in plain words to build an app, and you test what it built. |
| **MCP** | Model Context Protocol: a standard way to connect an AI to tools. |
| **host** | The app you talk to, for example ChatGPT or Claude Code; it passes messages between you, the model and the tools. |
| **model** | The AI that reads your question and writes the answer, for example Gemini or Claude Haiku. |
| **tool** | A small program on an MCP server that the AI can use, for example to count shipments. |

## The app in your browser (block 2)

No installation and no account: Streamlit (a Python tool for small web apps) runs inside the browser ([stlite](https://github.com/whitphx/stlite)). Notebook 2 tells you when to use these links.

- [Starter](https://edit.share.stlite.net/#!ChBzdHJlYW1saXRfYXBwLnB5Eq8EChBzdHJlYW1saXRfYXBwLnB5EpoECpcEIiIiU3RhcnRlcjogcHJvdmVzIHRoYXQgdGhlIGRhdGEgY29ubmVjdGlvbiB3b3Jrcy4gUmVwbGFjZSBhbGwgb2YgdGhpcyB3aXRoIHlvdXIgQUkncyBhcHAuIiIiCgppbXBvcnQgcGFuZGFzIGFzIHBkCmltcG9ydCBzdHJlYW1saXQgYXMgc3QKCkRBVEFfVVJMID0gImh0dHBzOi8vcmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbS9GSC1QcmV2YWlsL2FpbGFiL21haW4vZGF0YS9zaGlwbWVudHNfMjAyNV9jbGVhbi5jc3YiCgpzdC50aXRsZSgiWW91ciBhcHAgZ29lcyBoZXJlIikKZGF0YSA9IHBkLnJlYWRfY3N2KERBVEFfVVJMKQpzdC5zdWNjZXNzKGYiVGhlIGRhdGEgY29ubmVjdGlvbiB3b3Jrczoge2xlbihkYXRhKTosfSBzaGlwbWVudHMgbG9hZGVkLiIpCnN0LndyaXRlKCJOb3cgc2VsZWN0IGV2ZXJ5dGhpbmcgaW4gdGhlIGVkaXRvciBvbiB0aGUgbGVmdCAoQ3RybCArIEEpLCBwYXN0ZSB0aGUgY29kZSB5b3VyIEFJIHdyb3RlLCAiCiAgICAgICAgICJhbmQgY2xpY2sgKipTYXZlKiouIikKc3QuZGF0YWZyYW1lKGRhdGEuaGVhZCgxMCkpCg,,): the app editor, with a small app that only loads the data. You replace its code with your AI's app and click **Save**.
- [Reference app](https://edit.share.stlite.net/#!ChBzdHJlYW1saXRfYXBwLnB5Esc3ChBzdHJlYW1saXRfYXBwLnB5ErI3Cq83IiIiQ2FycmllciBTY29yZWNhcmQ6IHdoaWNoIGNhcnJpZXIga2VlcHMgaXRzIHByb21pc2UsIGJ5IGNvdW50cnkgYW5kIHNlcnZpY2U_CgpUaGUgcmVmZXJlbmNlIGFwcCBmb3IgaGFuZHMtb24gMiBvZiB0aGUgQUkgTGFiIHNlc3Npb24uIEl0IHJlYWRzIHRoZSBjbGVhbmVkCnNoaXBtZW50cyB0YWJsZSAodGhlIG1ldHJpYyBjb250cmFjdCBpcyBhbHJlYWR5IGFwcGxpZWQgdGhlcmUpLCBzbyBldmVyeSBLUEkgaXMgYQpwbGFpbiBhdmVyYWdlOgoKICAgIG9uLXRpbWUgcmF0ZSAgID0gYXZlcmFnZSBvZiBvbl90aW1lICAgICAgICgxIG9uIHRpbWUsIDAgbGF0ZSBvciBsb3N0LCBlbXB0eSA9IG5vdCBrbm93biB5ZXQpCiAgICB0cmFuc2l0IGRheXMgICA9IGF2ZXJhZ2Ugb2YgdHJhbnNpdF9kYXlzICAoZW1wdHkgdW5sZXNzIGRlbGl2ZXJlZCkKICAgIGNvc3Qvc2hpcG1lbnQgID0gYXZlcmFnZSBvZiBjb3N0X2V1cgogICAgZGFtYWdlIHJhdGUgICAgPSBhdmVyYWdlIG9mIGRhbWFnZWQgICAgICAgKGVtcHR5IHVubGVzcyBkZWxpdmVyZWQpCgpSdW4gaXQgaW4gdGhlIGJyb3dzZXI6IHBhc3RlIHRoaXMgZmlsZSBpbnRvIGh0dHBzOi8vZWRpdC5zaGFyZS5zdGxpdGUubmV0ClJ1biBpdCBvbiB5b3VyIGNvbXB1dGVyOiBwaXAgaW5zdGFsbCBzdHJlYW1saXQgcGFuZGFzIGFsdGFpciwgdGhlbiBzdHJlYW1saXQgcnVuIGFwcC5weQoiIiIKCmZyb20gcGF0aGxpYiBpbXBvcnQgUGF0aAoKaW1wb3J0IGFsdGFpciBhcyBhbHQKaW1wb3J0IHBhbmRhcyBhcyBwZAppbXBvcnQgc3RyZWFtbGl0IGFzIHN0CgpEQVRBX1VSTCA9ICJodHRwczovL3Jhdy5naXRodWJ1c2VyY29udGVudC5jb20vRkgtUHJldmFpbC9haWxhYi9tYWluL2RhdGEvc2hpcG1lbnRzXzIwMjVfY2xlYW4uY3N2IgpMT0NBTF9GSUxFID0gUGF0aChfX2ZpbGVfXykucmVzb2x2ZSgpLnBhcmVudC5wYXJlbnQgLyAiZGF0YSIgLyAic2hpcG1lbnRzXzIwMjVfY2xlYW4uY3N2IgpNSU5fUkVTT0xWRUQgPSAzMCAgICMgZmV3ZXIgcmVzb2x2ZWQgc2hpcG1lbnRzIHRoYW4gdGhpczogdG9vIGZldyB0byByZWNvbW1lbmQgYSBjYXJyaWVyCgpDT1VOVFJJRVMgPSB7IkFUIjogIkF1c3RyaWEiLCAiREUiOiAiR2VybWFueSIsICJDWiI6ICJDemVjaGlhIiwgIkhVIjogIkh1bmdhcnkiLCAiSVQiOiAiSXRhbHkiLCAiU0kiOiAiU2xvdmVuaWEifQpDT0xPUlMgPSB7IkJpYmVyIEZyZWlnaHQiOiAiIzBCNUNBRCIsICJGYWxrZSBUcmFuc3BvcnQiOiAiI0U2NkExRiIsICJHYW1zIENhcmdvIjogIiMxQjlFNUEiLAogICAgICAgICAgIkx1Y2hzIExvZ2lzdGlrIjogIiNEMDRGOTUifQpNT05USFMgPSBbIkphbiIsICJGZWIiLCAiTWFyIiwgIkFwciIsICJNYXkiLCAiSnVuIiwgIkp1bCIsICJBdWciLCAiU2VwIiwgIk9jdCIsICJOb3YiLCAiRGVjIl0KCgpAc3QuY2FjaGVfZGF0YQpkZWYgbG9hZF9kYXRhKCkgLT4gcGQuRGF0YUZyYW1lOgogICAgIiIiVGhlIGNsZWFuZWQgdGFibGU6IGZyb20gdGhlIGNvdXJzZSByZXBvc2l0b3J5LCBvciBmcm9tIHRoZSBkYXRhIGZvbGRlciBpZiBpdCBpcyBuZXh0IHRvIHRoZSBhcHAuIiIiCiAgICBzb3VyY2UgPSBMT0NBTF9GSUxFIGlmIExPQ0FMX0ZJTEUuZXhpc3RzKCkgZWxzZSBEQVRBX1VSTAogICAgcmV0dXJuIHBkLnJlYWRfY3N2KHNvdXJjZSwgcGFyc2VfZGF0ZXM9WyJzaGlwX2RhdGUiLCAicHJvbWlzZWRfZGF0ZSIsICJkZWxpdmVyZWRfZGF0ZSJdKQoKCmRlZiBzY29yZWNhcmQoZGY6IHBkLkRhdGFGcmFtZSkgLT4gcGQuRGF0YUZyYW1lOgogICAgIiIiT25lIHJvdyBwZXIgY2FycmllciB3aXRoIHRoZSBmaXZlIEtQSXMgb2YgdGhlIG1ldHJpYyBjb250cmFjdC4iIiIKICAgIHRhYmxlID0gZGYuZ3JvdXBieSgiY2FycmllciIpLmFnZygKICAgICAgICBzaGlwbWVudHM9KCJzaGlwbWVudF9pZCIsICJjb3VudCIpLAogICAgICAgIHJlc29sdmVkPSgib25fdGltZSIsICJjb3VudCIpLCAgICAgICAgICAgICAgICAgIyBjb3VudCgpIHNraXBzIGVtcHR5IGNlbGxzOiB0aGUgJ25vdCBrbm93biB5ZXQnIG9uZXMKICAgICAgICBvbl90aW1lX3BjdD0oIm9uX3RpbWUiLCAibWVhbiIpLAogICAgICAgIHRyYW5zaXRfZGF5cz0oInRyYW5zaXRfZGF5cyIsICJtZWFuIiksCiAgICAgICAgY29zdF9ldXI9KCJjb3N0X2V1ciIsICJtZWFuIiksCiAgICAgICAgZGFtYWdlX3BjdD0oImRhbWFnZWQiLCAibWVhbiIpLAogICAgKQogICAgdGFibGVbIm9uX3RpbWVfcGN0Il0gPSAodGFibGVbIm9uX3RpbWVfcGN0Il0gKiAxMDApLnJvdW5kKDEpCiAgICB0YWJsZVsiZGFtYWdlX3BjdCJdID0gKHRhYmxlWyJkYW1hZ2VfcGN0Il0gKiAxMDApLnJvdW5kKDEpCiAgICB0YWJsZVsidHJhbnNpdF9kYXlzIl0gPSB0YWJsZVsidHJhbnNpdF9kYXlzIl0ucm91bmQoMikKICAgIHRhYmxlWyJjb3N0X2V1ciJdID0gdGFibGVbImNvc3RfZXVyIl0ucm91bmQoMikKICAgIHJldHVybiB0YWJsZS5zb3J0X3ZhbHVlcygib25fdGltZV9wY3QiLCBhc2NlbmRpbmc9RmFsc2UpCgoKc3Quc2V0X3BhZ2VfY29uZmlnKHBhZ2VfdGl0bGU9IkNhcnJpZXIgU2NvcmVjYXJkIiwgbGF5b3V0PSJ3aWRlIikKc3QudGl0bGUoIkNhcnJpZXIgU2NvcmVjYXJkIikKc3QuY2FwdGlvbigiU2hpcG1lbnRzIG9mIDIwMjUsIGNsZWFuZWQgd2l0aCB0aGUgbWV0cmljIGNvbnRyYWN0LiBQaWNrIGEgY291bnRyeSBhbmQgYSBzZXJ2aWNlIG9uIHRoZSBsZWZ0LiIpCgpkYXRhID0gbG9hZF9kYXRhKCkKCiMgLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLSB0aGUgZmlsdGVycwp3aXRoIHN0LnNpZGViYXI6CiAgICBzdC5oZWFkZXIoIllvdXIgc2VsZWN0aW9uIikKICAgIGNvdW50cnkgPSBzdC5zZWxlY3Rib3goIkRlc3RpbmF0aW9uIGNvdW50cnkiLCBbIkFsbCBjb3VudHJpZXMiXSArIGxpc3QoQ09VTlRSSUVTKSwKICAgICAgICAgICAgICAgICAgICAgICAgICAgZm9ybWF0X2Z1bmM9bGFtYmRhIGM6IENPVU5UUklFUy5nZXQoYywgYykpCiAgICBzZXJ2aWNlID0gc3QucmFkaW8oIlNlcnZpY2UiLCBbIkFsbCBzZXJ2aWNlcyIsICJTdGFuZGFyZCIsICJFeHByZXNzIl0pCiAgICBmaXJzdCwgbGFzdCA9IHN0LnNlbGVjdF9zbGlkZXIoIk1vbnRocyIsIG9wdGlvbnM9bGlzdChyYW5nZSgxLCAxMykpLCB2YWx1ZT0oMSwgMTIpLAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIGZvcm1hdF9mdW5jPWxhbWJkYSBtOiBNT05USFNbbSAtIDFdKQoKc2VsZWN0aW9uID0gZGF0YVtkYXRhWyJtb250aCJdLmJldHdlZW4oZmlyc3QsIGxhc3QpXQppZiBjb3VudHJ5ICE9ICJBbGwgY291bnRyaWVzIjoKICAgIHNlbGVjdGlvbiA9IHNlbGVjdGlvbltzZWxlY3Rpb25bImNvdW50cnkiXSA9PSBjb3VudHJ5XQppZiBzZXJ2aWNlICE9ICJBbGwgc2VydmljZXMiOgogICAgc2VsZWN0aW9uID0gc2VsZWN0aW9uW3NlbGVjdGlvblsic2VydmljZSJdID09IHNlcnZpY2VdCgp3aGVyZSA9IENPVU5UUklFUy5nZXQoY291bnRyeSwgIkFsbCBjb3VudHJpZXMiKQptb250aHMgPSBNT05USFNbZmlyc3QgLSAxXSBpZiBmaXJzdCA9PSBsYXN0IGVsc2UgZiJ7TU9OVEhTW2ZpcnN0IC0gMV19IHRvIHtNT05USFNbbGFzdCAtIDFdfSIKc3Quc3ViaGVhZGVyKGYie3doZXJlfSwge3NlcnZpY2UubG93ZXIoKX0sIHttb250aHN9IikKCiMgLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLSB0aGUgYW5zd2VyCmlmIHNlbGVjdGlvbi5lbXB0eToKICAgIHN0Lndhcm5pbmcoIk5vIHNoaXBtZW50cyBmb3IgdGhpcyBzZWxlY3Rpb24uIikKICAgIHN0LnN0b3AoKQoKdGFibGUgPSBzY29yZWNhcmQoc2VsZWN0aW9uKQplbGlnaWJsZSA9IHRhYmxlW3RhYmxlWyJyZXNvbHZlZCJdID49IE1JTl9SRVNPTFZFRF0KaWYgZWxpZ2libGUuZW1wdHk6CiAgICBzdC5pbmZvKGYiVG9vIGZldyBzaGlwbWVudHMgdG8gcmVjb21tZW5kIGEgY2Fycmllcjogbm9uZSBoYXMge01JTl9SRVNPTFZFRH0gb3IgbW9yZSB3aXRoIGEga25vd24gcmVzdWx0LiIpCmVsc2U6CiAgICB0b3AgPSBlbGlnaWJsZS5pbmRleFswXQogICAgc3Quc3VjY2VzcyhmIk1vc3Qgb2Z0ZW4gb24gdGltZTogKip7dG9wfSoqLCB7ZWxpZ2libGUubG9jW3RvcCwgJ29uX3RpbWVfcGN0J106LjFmfSAlICIKICAgICAgICAgICAgICAgZiJvZiB7aW50KGVsaWdpYmxlLmxvY1t0b3AsICdyZXNvbHZlZCddKX0gc2hpcG1lbnRzIHdpdGggYSBrbm93biByZXN1bHQuIikKCnNob3duID0gdGFibGUucmVuYW1lKGNvbHVtbnM9ewogICAgInNoaXBtZW50cyI6ICJTaGlwbWVudHMiLCAicmVzb2x2ZWQiOiAiS25vd24gcmVzdWx0IiwgIm9uX3RpbWVfcGN0IjogIk9uIHRpbWUgJSIsCiAgICAidHJhbnNpdF9kYXlzIjogIlRyYW5zaXQgZGF5cyIsICJjb3N0X2V1ciI6ICJDb3N0IHBlciBzaGlwbWVudCDigqwiLCAiZGFtYWdlX3BjdCI6ICJEYW1hZ2VkICUifSkKc2hvd24uaW5kZXgubmFtZSA9ICJDYXJyaWVyIgpzdC5kYXRhZnJhbWUoc2hvd24sIHdpZHRoPSJzdHJldGNoIikKCm1pc3NpbmcgPSBbY2FycmllciBmb3IgY2FycmllciBpbiBDT0xPUlMgaWYgY2FycmllciBub3QgaW4gdGFibGUuaW5kZXhdCmlmIG1pc3Npbmc6CiAgICBzdC5jYXB0aW9uKGYiTm8gc2hpcG1lbnRzIGluIHRoaXMgc2VsZWN0aW9uOiB7JywgJy5qb2luKG1pc3NpbmcpfS4iKQpub3Rfa25vd24gPSBpbnQodGFibGVbInNoaXBtZW50cyJdLnN1bSgpIC0gdGFibGVbInJlc29sdmVkIl0uc3VtKCkpCmlmIG5vdF9rbm93bjoKICAgIHN0LmNhcHRpb24oZiJ7bm90X2tub3dufSBzaGlwbWVudHMgd2VyZSBzdGlsbCBvbiB0aGVpciB3YXkgYXQgdGhlIGVuZCBvZiB0aGUgZXhwb3J0IHdpdGggdGhlIHByb21pc2VkICIKICAgICAgICAgICAgICAgImRhdGUgYWhlYWQ7IHRoZXkgYXJlIGxlZnQgb3V0IG9mIHRoZSBvbi10aW1lIHJhdGUuIikKCmxlZnQsIHJpZ2h0ID0gc3QuY29sdW1ucygyKQp3aXRoIGxlZnQ6CiAgICBzdC5tYXJrZG93bigiKipPbiB0aW1lICUqKiIpCiAgICBiYXJzID0gYWx0LkNoYXJ0KHRhYmxlLnJlc2V0X2luZGV4KCkpLm1hcmtfYmFyKCkuZW5jb2RlKAogICAgICAgIHg9YWx0LlgoIm9uX3RpbWVfcGN0OlEiLCB0aXRsZT0iT24gdGltZSAlIiwgc2NhbGU9YWx0LlNjYWxlKGRvbWFpbj1bMCwgMTAwXSkpLAogICAgICAgIHk9YWx0LlkoImNhcnJpZXI6TiIsIHRpdGxlPU5vbmUsIHNvcnQ9Ii14IiksCiAgICAgICAgY29sb3I9YWx0LkNvbG9yKCJjYXJyaWVyOk4iLCBzY2FsZT1hbHQuU2NhbGUoZG9tYWluPWxpc3QoQ09MT1JTKSwgcmFuZ2U9bGlzdChDT0xPUlMudmFsdWVzKCkpKSwKICAgICAgICAgICAgICAgICAgICAgICAgbGVnZW5kPU5vbmUpLAogICAgICAgIHRvb2x0aXA9WyJjYXJyaWVyIiwgIm9uX3RpbWVfcGN0IiwgInJlc29sdmVkIl0sCiAgICApCiAgICBzdC5hbHRhaXJfY2hhcnQoYmFycywgd2lkdGg9InN0cmV0Y2giKQp3aXRoIHJpZ2h0OgogICAgc3QubWFya2Rvd24oIioqT24gdGltZSAlIGJ5IG1vbnRoKioiKQogICAgbW9udGhseSA9IChzZWxlY3Rpb24uZHJvcG5hKHN1YnNldD1bIm9uX3RpbWUiXSkuZ3JvdXBieShbIm1vbnRoIiwgImNhcnJpZXIiXSlbIm9uX3RpbWUiXS5tZWFuKCkgKiAxMDApCiAgICBtb250aGx5ID0gbW9udGhseS5yb3VuZCgxKS5yZXNldF9pbmRleChuYW1lPSJvbl90aW1lX3BjdCIpCiAgICBtb250aGx5WyJtb250aF9uYW1lIl0gPSBbTU9OVEhTW20gLSAxXSBmb3IgbSBpbiBtb250aGx5WyJtb250aCJdXQogICAgbGluZXMgPSBhbHQuQ2hhcnQobW9udGhseSkubWFya19saW5lKHBvaW50PVRydWUpLmVuY29kZSgKICAgICAgICB4PWFsdC5YKCJtb250aF9uYW1lOk8iLCB0aXRsZT1Ob25lLCBzb3J0PU1PTlRIUyksCiAgICAgICAgeT1hbHQuWSgib25fdGltZV9wY3Q6USIsIHRpdGxlPSJPbiB0aW1lICUiLCBzY2FsZT1hbHQuU2NhbGUoemVybz1GYWxzZSkpLAogICAgICAgIGNvbG9yPWFsdC5Db2xvcigiY2FycmllcjpOIiwgc2NhbGU9YWx0LlNjYWxlKGRvbWFpbj1saXN0KENPTE9SUyksIHJhbmdlPWxpc3QoQ09MT1JTLnZhbHVlcygpKSksCiAgICAgICAgICAgICAgICAgICAgICAgIHRpdGxlPU5vbmUpLAogICAgICAgIHRvb2x0aXA9WyJjYXJyaWVyIiwgIm1vbnRoX25hbWUiLCAib25fdGltZV9wY3QiXSwKICAgICkKICAgIHN0LmFsdGFpcl9jaGFydChsaW5lcywgd2lkdGg9InN0cmV0Y2giKQoKd2l0aCBzdC5leHBhbmRlcigiSG93IHRoZSBudW1iZXJzIGFyZSBtYWRlIik6CiAgICBzdC5tYXJrZG93bigKICAgICAgICAiLSBPbmUgcm93IHBlciBzaGlwbWVudDsgY2FycmllciBuYW1lcyBjbGVhbmVkOyBXZWxzIHdlaWdodHMgZnJvbSBTZXB0ZW1iZXIgY29udmVydGVkIGZyb20gZ3JhbXMuXG4iCiAgICAgICAgIi0gKipPbiB0aW1lKio6IGRlbGl2ZXJlZCBvbiBvciBiZWZvcmUgdGhlIHByb21pc2VkIGRhdGUuIExvc3QgY291bnRzIGFzIGxhdGUuIFN0aWxsIG9uIGl0cyB3YXkgd2l0aCAiCiAgICAgICAgInRoZSBwcm9taXNlZCBkYXRlIHBhc3NlZCBjb3VudHMgYXMgbGF0ZS4gU3RpbGwgb24gaXRzIHdheSB3aXRoIHRoZSBwcm9taXNlZCBkYXRlIGFoZWFkIGlzIG5vdCBrbm93biAiCiAgICAgICAgInlldCBhbmQgbGVmdCBvdXQuXG4iCiAgICAgICAgIi0gKipUcmFuc2l0IGRheXMqKjogY2FsZW5kYXIgZGF5cyBmcm9tIHNoaXBwaW5nIHRvIGRlbGl2ZXJ5LCBkZWxpdmVyZWQgc2hpcG1lbnRzIG9ubHkuXG4iCiAgICAgICAgIi0gKipEYW1hZ2VkICUqKjogZGFtYWdlZCBzaGlwbWVudHMgYW1vbmcgZGVsaXZlcmVkIG9uZXMuICoqQ29zdCoqOiBhdmVyYWdlIGNvc3QgcGVyIHNoaXBtZW50LlxuIgogICAgICAgIGYiLSBBIGNhcnJpZXIgaXMgcmVjb21tZW5kZWQgb25seSB3aXRoIGF0IGxlYXN0IHtNSU5fUkVTT0xWRUR9IHNoaXBtZW50cyB3aXRoIGEga25vd24gcmVzdWx0LlxuIgogICAgICAgICItIFRoZXNlIGFyZSBvYnNlcnZhdGlvbnMgZnJvbSAyMDI1LCBhIHN0YXJ0aW5nIHBvaW50IGZvciB0aGUgMjAyNyBjb250cmFjdHMsIG5vdCBwcm9vZi4iCiAgICApCg,,): our version, if you are stuck. Its code is [app/app.py](app/app.py).
- [An app with one wrong line](app/buggy_app.py): test it and find the line.

The first time, the starter can take up to a minute to load.

## Gemini API key (optional, notebook 3)

The key is free in Google AI Studio. The free version (free tier) allows only a limited number of requests per minute and per day. The limits change, so check them in AI Studio (checked 16 November 2026). Store the key as a Colab secret, never in a cell or a prompt. Your questions and the tool results in notebook 3 go to Google; the app in your browser stays in your browser.

## Slides

[The slides as PDF](slides/AI_Lab_Vibe_Analytics_Coding_MCP.pdf)

---

## For later (not needed in class)

### The data

The data is not real (it is synthetic), but it is built like a real export. The company and the four carriers are invented. [data/README.md](data/README.md) describes every column.

| File | What it is | Used in |
|---|---|---|
| [shipments_2025.csv](data/shipments_2025.csv) | the raw export: 6,043 rows, every shipment of 2025, problems included | notebook 1 |
| [shipments_2025_clean.csv](data/shipments_2025_clean.csv) | the same shipments after the metric contract: 5,918 rows | notebooks 2 and 3, the app, Power BI |
| [carrier_notes.csv](data/carrier_notes.csv) | 14 notes our teams wrote about the carriers | notebook 3 (the MCP server) |

Download a file with the **Download raw file** button on its GitHub page.

### The app and the MCP server on your own computer

- **The app:** `pip install streamlit pandas altair`, then `streamlit run app/app.py`.
- **The MCP server:** [mcp_server/shipments_server.py](mcp_server/shipments_server.py) gives any MCP host four read-only tools (they read the cleaned table, but never change it): `list_carriers`, `carrier_scorecard`, `late_shipments`, `carrier_notes`. It needs `pip install "mcp==2.3.0" pandas` and reads the data from a `data/` folder next to it, or from this repository.
  - **Claude Code:** `claude mcp add shipments -- python mcp_server/shipments_server.py`
  - **Claude Desktop, Gemini CLI, VS Code, LM Studio:** add a server with command `python` and argument `path/to/shipments_server.py` in the host's MCP settings.

Any MCP host that can start a local program and is allowed to do so can use it. [traces/](traces/) holds four real recordings of a model using these tools (question, tool calls, results, answer), also as a readable [worksheet](traces/README.md).

### Power BI

The demo of block 2 uses the app's KPI definitions (KPIs: key numbers such as on time %) again in Power BI, with Microsoft's Power BI MCP server: [powerbi/README.md](powerbi/README.md), with the prompts and the DAX measures. It needs Windows and Power BI Desktop.

### How the numbers were made

`data/make_dataset.py` makes the data (fixed seed, identical files every time). `analysis/build_evidence.py` applies the metric contract and writes every number the slides, notebooks and checks show into `evidence/results.json` and `evidence/check_table.csv`. It stops if a result that the session teaches is no longer true. `scripts/test_app.py` and `scripts/test_mcp.py` check the app and the MCP server against the same table.

```bash
python3 -m pip install -r requirements.txt
python3 data/make_dataset.py
python3 analysis/build_evidence.py
python3 scripts/test_app.py
python3 scripts/test_mcp.py
```

## After the session: what we found

<details>
<summary>Open this after the session: it shows the answer to notebook 1.</summary>

On time, by country (the metric contract, shipments with a known result):

| Country | Most often on time | Second | Shipments with a known result (first carrier) |
|---|---|---|---|
| Austria | Gams Cargo, 98.9 % | Falke Transport, 95.4 % | 186 |
| Germany | Luchs Logistik, 89.1 % | Falke Transport, 86.8 % | 626 |
| Czechia | Falke Transport, 90.2 % | Luchs Logistik, 87.5 % | 61 |
| Hungary | Gams Cargo, 88.5 % | Biber Freight, 77.2 % | 288 |
| Italy | Gams Cargo, 85.1 % | Biber Freight, 75.0 % | 429 |
| Slovenia | Gams Cargo, 88.4 % | Biber Freight, 87.1 % | 215 |

These are observations from 2025: a starting point for the 2027 contracts, not proof. Groups with only a few shipments, and carriers with very similar results, need more data. Recent months matter.

</details>

Free to use for teaching. Synthetic data; no real company is described.
