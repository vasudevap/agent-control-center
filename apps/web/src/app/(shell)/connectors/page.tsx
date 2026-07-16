import { CONNECTOR_FIXTURES } from "./connector-data";
import { ConnectorsWorkspace } from "./connectors-workspace";

export default function ConnectorsPage() {
  return <ConnectorsWorkspace connectors={CONNECTOR_FIXTURES} />;
}
