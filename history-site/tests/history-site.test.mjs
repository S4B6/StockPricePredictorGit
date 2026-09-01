import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

const workerUrl = new URL("../dist/server/index.js", import.meta.url);
workerUrl.searchParams.set("test", `${process.pid}-${Date.now()}`);
const { default: worker } = await import(workerUrl.href);

const executionContext = {
  waitUntil() {},
  passThroughOnException() {},
};

async function request(path) {
  return worker.fetch(
    new Request(`https://markets.example${path}`, {
      headers: { accept: "text/html" },
    }),
    {
      ASSETS: { fetch: async () => new Response("Not found", { status: 404 }) },
    },
    executionContext,
  );
}

test("root sends visitors to History", async () => {
  const response = await request("/");
  assert.equal(response.status, 307);
  assert.equal(response.headers.get("location"), "https://markets.example/history");
});

test("renders the landing page and all published policy-rate articles", async () => {
  const routes = new Map([
    ["/history", "Decades of data"],
    ["/history/rates/policy-rates/fed", "Fed Policy Rates"],
    ["/history/rates/policy-rates/ecb", "ECB Policy Rates"],
    ["/history/rates/policy-rates/key-global-policy-rates", "Key Global Policy Rates"],
  ]);

  for (const [path, expected] of routes) {
    const response = await request(path);
    assert.equal(response.status, 200, path);
    assert.match(response.headers.get("content-type") ?? "", /^text\/html\b/i, path);
    assert.match(await response.text(), new RegExp(expected), path);
  }
});

test("publishes only the three real fixture pages", async () => {
  const path = new URL("../app/data/history-pages.json", import.meta.url);
  const pages = JSON.parse(await readFile(path, "utf8"));
  assert.deepEqual(
    pages.map((page) => page.slug).sort(),
    [
      "rates/policy-rates/ecb",
      "rates/policy-rates/fed",
      "rates/policy-rates/key-global-policy-rates",
    ],
  );
  assert.doesNotMatch(JSON.stringify(pages), /ΓÇ|Γå/);
});

test("includes the committed global-rates snapshot", async () => {
  const path = new URL("../public/data/global-rates.csv", import.meta.url);
  const csv = await readFile(path, "utf8");
  const lines = csv.trim().split(/\r?\n/);
  assert.equal(lines[0], "date,AONIA,CALL_RATE,CHINA_FR001,CORRA,EONIA,ESTER,FFER,NOWA,SARON,SONIA");
  assert.equal(lines[1].slice(0, 10), "1999-01-01");
  assert.equal(lines.at(-1).slice(0, 10), "2025-11-07");
});
