import { findArtifactById } from "../artifact-data";
import { ArtifactDetailWorkspace } from "./artifact-detail-workspace";

export default async function ArtifactDetailPage({
  params,
}: {
  params: Promise<{ artifactId: string }>;
}) {
  const { artifactId } = await params;
  return (
    <ArtifactDetailWorkspace
      artifact={findArtifactById(artifactId)}
      requestedId={artifactId}
    />
  );
}
