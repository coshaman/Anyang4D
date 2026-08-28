export type ReleaseVersion = {
  git_commit: string;
  build_timestamp: string;
  frontend_build_id: string;
  api_schema_version: string;
  scenario_schema_version: string;
};

export const FRONTEND_BUILD_ID = import.meta.env.VITE_FRONTEND_BUILD_ID || "local-dev";
