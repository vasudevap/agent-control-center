import { ARTIFACT_FIXTURES, findArtifactById } from "../artifact-data";
import { ArtifactDetailWorkspace } from "./artifact-detail-workspace";

export function generateStaticParams() {
  return ARTIFACT_FIXTURES.map((artifact) => ({ artifactId: artifact.id }));
}

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
