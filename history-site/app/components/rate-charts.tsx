"use client";

import { useEffect, useMemo, useState } from "react";
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Scatter,
  ScatterChart,
  Tooltip,
  XAxis,
  YAxis,
  ZAxis,
} from "recharts";

type RateRow = {
  date: string;
  [indicator: string]: string | number | null;
};

type RateStat = {
  indicator_code: string;
  mean: number;
  std: number;
  avg_corr: number;
  avg_abs_corr: number;
};

const SERIES = [
  "AONIA",
  "CALL_RATE",
  "CHINA_FR001",
  "CORRA",
  "EONIA",
  "ESTER",
  "FFER",
  "NOWA",
  "SARON",
  "SONIA",
] as const;

const COLORS: Record<string, string> = {
  AONIA: "#ff8000",
  CALL_RATE: "#ffea00",
  CHINA_FR001: "#ff4040",
  CORRA: "#3bd5ff",
  EONIA: "#c776ff",
  ESTER: "#ff00b8",
  FFER: "#55ff8b",
  NOWA: "#9da7ff",
  SARON: "#ffffff",
  SONIA: "#00fff7",
};

const LABELS: Record<string, string> = {
  AONIA: "Australia · AONIA",
  CALL_RATE: "Japan · Call rate",
  CHINA_FR001: "China · FR001",
  CORRA: "Canada · CORRA",
  EONIA: "Euro area · EONIA",
  ESTER: "Euro area · €STR",
  FFER: "United States · EFFR",
  NOWA: "Norway · NOWA",
  SARON: "Switzerland · SARON",
  SONIA: "United Kingdom · SONIA",
};

function parseCsv<T>(text: string, rowParser: (cells: string[], headers: string[]) => T): T[] {
  const [headerLine, ...lines] = text.trim().split(/\r?\n/);
  const headers = headerLine.split(",");
  return lines.filter(Boolean).map((line) => rowParser(line.split(","), headers));
}

function parseRateRows(text: string) {
  return parseCsv<RateRow>(text, (cells, headers) => {
    const row: RateRow = { date: cells[0] };
    headers.slice(1).forEach((header, index) => {
      const raw = cells[index + 1];
      row[header] = raw === "" || raw === undefined ? null : Number(raw);
    });
    return row;
  });
}

function parseStats(text: string) {
  return parseCsv<RateStat>(text, (cells, headers) => {
    const record = Object.fromEntries(headers.map((header, index) => [header, cells[index]]));
    return {
      indicator_code: record.indicator_code,
      mean: Number(record.mean),
      std: Number(record.std),
      avg_corr: Number(record.avg_corr),
      avg_abs_corr: Number(record.avg_abs_corr),
    };
  });
}

function monthlySample<T extends { date: string }>(rows: T[]) {
  const sampled: T[] = [];
  let activeMonth = "";
  for (const row of rows) {
    const month = row.date.slice(0, 7);
    if (month !== activeMonth) {
      sampled.push(row);
      activeMonth = month;
    } else {
      sampled[sampled.length - 1] = row;
    }
  }
  return sampled;
}

function mean(values: number[]) {
  return values.reduce((sum, value) => sum + value, 0) / values.length;
}

function median(values: number[]) {
  const sorted = [...values].sort((a, b) => a - b);
  const middle = Math.floor(sorted.length / 2);
  return sorted.length % 2 ? sorted[middle] : (sorted[middle - 1] + sorted[middle]) / 2;
}

function derivedSeries(rows: RateRow[]) {
  const composites: { date: string; value: number }[] = [];
  const dispersion: { date: string; value: number }[] = [];
  const rolling: number[] = [];

  for (const row of rows) {
    const allValues = SERIES.map((series) => row[series]).filter(
      (value): value is number => typeof value === "number" && Number.isFinite(value),
    );
    if (allValues.length >= 4) {
      rolling.push(mean(allValues));
      if (rolling.length > 5) rolling.shift();
      composites.push({ date: row.date, value: mean(rolling) });
    }

    const coreValues = SERIES.filter(
      (series) => series !== "CALL_RATE" && series !== "CHINA_FR001",
    )
      .map((series) => row[series])
      .filter((value): value is number => typeof value === "number" && Number.isFinite(value));
    if (coreValues.length >= 4) {
      const center = median(coreValues);
      dispersion.push({
        date: row.date,
        value: mean(coreValues.map((value) => Math.abs(value - center))),
      });
    }
  }

  return {
    composite: monthlySample(composites),
    dispersion: monthlySample(dispersion),
  };
}

function formatTick(date: string) {
  return date.slice(0, 4);
}

function ChartLoading() {
  return <div className="chart-state"><span className="loading-dot" />Loading the committed data snapshot…</div>;
}

function ChartError() {
  return <div className="chart-state error">The chart snapshot could not be loaded. The article remains available.</div>;
}

function ChartFrame({
  title,
  description,
  children,
}: {
  title: string;
  description: string;
  children: React.ReactNode;
}) {
  return (
    <section className="chart-frame" aria-label={title}>
      <div className="chart-heading">
        <div>
          <p className="chart-eyebrow">Committed snapshot</p>
          <h3>{title}</h3>
          <p>{description}</p>
        </div>
        <a className="download-link" href="/data/global-rates.csv" download>
          CSV <span aria-hidden="true">↓</span>
        </a>
      </div>
      {children}
      <p className="chart-source">Source snapshot in the original repository · through 7 November 2025</p>
    </section>
  );
}

export function DataRestorationNotice({ institution }: { institution: string }) {
  return (
    <section className="chart-frame restoration-card">
      <div className="restoration-signal" aria-hidden="true" />
      <div>
        <p className="chart-eyebrow">Data restoration queued</p>
        <h3>{institution} historical policy-rate chart</h3>
        <p>
          The article is recovered and public. Its exact target/facility-rate series was stored in the former database and is not present in GitHub, so the chart is deliberately not approximated.
        </p>
      </div>
    </section>
  );
}

export function GlobalRateChart({ index }: { index: number }) {
  const [rows, setRows] = useState<RateRow[] | null>(null);
  const [stats, setStats] = useState<RateStat[] | null>(null);
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    let cancelled = false;
    Promise.all([
      fetch("/data/global-rates.csv").then((response) => {
        if (!response.ok) throw new Error("rates");
        return response.text();
      }),
      fetch("/data/global-rate-stats.csv").then((response) => {
        if (!response.ok) throw new Error("stats");
        return response.text();
      }),
    ])
      .then(([rateText, statsText]) => {
        if (cancelled) return;
        setRows(parseRateRows(rateText));
        setStats(parseStats(statsText));
      })
      .catch(() => {
        if (!cancelled) setFailed(true);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const sampledRows = useMemo(() => (rows ? monthlySample(rows) : []), [rows]);
  const derived = useMemo(() => (rows ? derivedSeries(rows) : null), [rows]);

  if (failed) return <ChartError />;
  if (!rows || !stats || !derived) return <ChartLoading />;

  if (index === 1) {
    const min = Math.min(...stats.map((item) => item.mean));
    const max = Math.max(...stats.map((item) => item.mean));
    return (
      <ChartFrame title="Average overnight rates" description="Long-run average by benchmark; colour intensity increases with the average rate.">
        <div className="rate-heatmap">
          {stats.map((item) => {
            const intensity = (item.mean - min) / Math.max(max - min, 0.01);
            return (
              <div
                className="heat-cell"
                key={item.indicator_code}
                style={{ "--heat-alpha": String(0.16 + intensity * 0.72) } as React.CSSProperties}
              >
                <span>{LABELS[item.indicator_code] ?? item.indicator_code}</span>
                <strong>{item.mean.toFixed(2)}%</strong>
              </div>
            );
          })}
        </div>
      </ChartFrame>
    );
  }

  if (index === 2) {
    const bubbleData = stats.map((item) => ({
      x: item.mean,
      y: item.std,
      z: 80 + item.avg_abs_corr * 580,
      name: LABELS[item.indicator_code] ?? item.indicator_code,
      code: item.indicator_code,
    }));
    return (
      <ChartFrame title="Rate profiles" description="Average level versus volatility; bubble size reflects average absolute correlation.">
        <div className="chart-canvas">
          <ResponsiveContainer width="100%" height="100%">
            <ScatterChart margin={{ top: 24, right: 24, bottom: 34, left: 12 }}>
              <CartesianGrid stroke="#ffffff18" strokeDasharray="3 5" />
              <XAxis type="number" dataKey="x" name="Mean" unit="%" stroke="#8e8e99" tick={{ fill: "#a9a9b2", fontSize: 12 }} label={{ value: "Average rate (%)", position: "bottom", fill: "#8e8e99" }} />
              <YAxis type="number" dataKey="y" name="Volatility" unit="%" stroke="#8e8e99" tick={{ fill: "#a9a9b2", fontSize: 12 }} label={{ value: "Volatility", angle: -90, position: "insideLeft", fill: "#8e8e99" }} />
              <ZAxis type="number" dataKey="z" range={[90, 650]} />
              <Tooltip cursor={{ strokeDasharray: "3 3" }} contentStyle={{ background: "#09080d", border: "1px solid #ff800066", color: "#fff" }} />
              <Scatter data={bubbleData} fill="#ff8000" fillOpacity={0.78} />
            </ScatterChart>
          </ResponsiveContainer>
        </div>
      </ChartFrame>
    );
  }

  if (index === 3) {
    return (
      <ChartFrame title="Daily rates through time" description="Monthly end observations sampled from the committed daily dataset for a readable long-run view.">
        <div className="chart-canvas chart-canvas-tall">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={sampledRows} margin={{ top: 12, right: 18, bottom: 16, left: 0 }}>
              <CartesianGrid stroke="#ffffff14" strokeDasharray="3 5" />
              <XAxis dataKey="date" minTickGap={56} tickFormatter={formatTick} stroke="#6f6f79" tick={{ fill: "#a9a9b2", fontSize: 11 }} />
              <YAxis unit="%" stroke="#6f6f79" tick={{ fill: "#a9a9b2", fontSize: 11 }} width={46} />
              <Tooltip labelFormatter={(label) => String(label)} contentStyle={{ background: "#09080d", border: "1px solid #ffffff25", color: "#fff" }} />
              <Legend wrapperStyle={{ fontSize: 11, paddingTop: 12 }} />
              {SERIES.map((series) => (
                <Line key={series} type="monotone" dataKey={series} name={series} stroke={COLORS[series]} strokeWidth={1.35} dot={false} connectNulls />
              ))}
            </LineChart>
          </ResponsiveContainer>
        </div>
      </ChartFrame>
    );
  }

  if (index === 4) {
    return (
      <ChartFrame title="Composite rate index" description="Five-day moving average of the cross-market overnight-rate mean.">
        <SingleSeriesChart data={derived.composite} color="#ff8000" />
      </ChartFrame>
    );
  }

  return (
    <ChartFrame title="Cross-market dispersion" description="Mean absolute distance from the cross-market median, excluding Japan and China.">
      <SingleSeriesChart data={derived.dispersion} color="#ff00b8" />
    </ChartFrame>
  );
}

function SingleSeriesChart({ data, color }: { data: { date: string; value: number }[]; color: string }) {
  return (
    <div className="chart-canvas">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data} margin={{ top: 12, right: 18, bottom: 10, left: 0 }}>
          <CartesianGrid stroke="#ffffff14" strokeDasharray="3 5" />
          <XAxis dataKey="date" minTickGap={56} tickFormatter={formatTick} stroke="#6f6f79" tick={{ fill: "#a9a9b2", fontSize: 11 }} />
          <YAxis unit="%" stroke="#6f6f79" tick={{ fill: "#a9a9b2", fontSize: 11 }} width={46} />
          <Tooltip contentStyle={{ background: "#09080d", border: "1px solid #ffffff25", color: "#fff" }} />
          <Line type="monotone" dataKey="value" stroke={color} strokeWidth={2} dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
