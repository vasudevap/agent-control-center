import assert from "node:assert/strict";
import test from "node:test";

async function render() {
  const workerUrl = new URL("../dist/server/index.js", import.meta.url);
  workerUrl.searchParams.set("test", `${process.pid}-${Date.now()}`);
  const { default: worker } = await import(workerUrl.href);

  return worker.fetch(
    new Request("http://atlas.test/", {
      headers: { accept: "text/html", host: "atlas.test" },
    }),
    {
      ASSETS: { fetch: async () => new Response("Not found", { status: 404 }) },
    },
    { waitUntil() {}, passThroughOnException() {} },
  );
}

test("renders the complete Atlas public-site narrative", async () => {
  const response = await render();
  assert.equal(response.status, 200);
  assert.match(response.headers.get("content-type") ?? "", /^text\/html\b/i);

  const html = await response.text();
  assert.match(html, /<title>Atlas \| Enterprise Agent Control Center<\/title>/i);
  assert.match(html, /Keep autonomous work under control/i);
  assert.match(html, /More agents should not mean less control/i);
  assert.match(html, /Human authority is part of the architecture/i);
  assert.match(html, /Built as a control plane, not a collection of scripts/i);
  assert.match(html, />Built</i);
  assert.match(html, />Designed</i);
  assert.match(html, />Planned</i);
  assert.match(html, /Product prototype and architecture reference/i);
  assert.doesNotMatch(html, /codex-preview|free trial|customer logos|sign up/i);
});

test("renders semantic navigation and a single page heading", async () => {
  const response = await render();
  const html = await response.text();
  const h1Count = (html.match(/<h1\b/gi) ?? []).length;

  assert.equal(h1Count, 1);
  assert.match(html, /<header\b/i);
  assert.match(html, /<nav\b[^>]*aria-label="Primary"/i);
  assert.match(html, /<main\b[^>]*id="main-content"/i);
  assert.match(html, /<footer\b/i);
  assert.match(html, /href="#main-content"/i);
  assert.match(html, /href="#product"/i);
  assert.match(html, /href="#architecture"/i);
  assert.match(html, /href="#status"/i);
});
