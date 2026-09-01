import { HistoryExplorer } from "../components/history-explorer";
import { SiteShell } from "../components/site-shell";
import { historyPages } from "../data/history";

export default function HistoryHome() {
  return (
    <SiteShell>
      <HistoryExplorer pages={historyPages} />
    </SiteShell>
  );
}
