/**
 * ConCOREdance Google Drive -> GitHub sync proof of concept.
 *
 * This Apps Script is intentionally conservative:
 * - allowlisted Drive root only
 * - dry-run mode by default
 * - content hash skip logic
 * - GitHub token stored in Script Properties
 *
 * Required Script Properties:
 *   GITHUB_TOKEN
 *   GITHUB_OWNER
 *   GITHUB_REPO
 *   GITHUB_BRANCH
 *   DRIVE_ROOT_FOLDER_ID
 *   GITHUB_TARGET_PREFIX
 *   SYNC_DRY_RUN
 */

const SUPPORTED_EXTENSIONS = [
  ".md",
  ".txt",
  ".json",
  ".html",
  ".css",
  ".js",
  ".png",
  ".jpg",
  ".jpeg",
  ".pdf",
];

function syncConCOREdanceDriveToGitHub() {
  const config = readSyncConfig_();
  const root = DriveApp.getFolderById(config.driveRootFolderId);
  const files = collectFiles_(root, "");
  const report = {
    created: [],
    updated: [],
    skipped: [],
    unsupported: [],
    failed: [],
  };

  files.forEach((item) => {
    try {
      const result = syncOneFile_(item, config);
      report[result.status].push(result.githubPath);
    } catch (error) {
      report.failed.push(`${item.relativePath}: ${error.message}`);
    }
  });

  Logger.log(JSON.stringify(report, null, 2));
  return report;
}

function readSyncConfig_() {
  const props = PropertiesService.getScriptProperties();
  const required = [
    "GITHUB_TOKEN",
    "GITHUB_OWNER",
    "GITHUB_REPO",
    "GITHUB_BRANCH",
    "DRIVE_ROOT_FOLDER_ID",
    "GITHUB_TARGET_PREFIX",
  ];
  const config = {};
  required.forEach((key) => {
    const value = props.getProperty(key);
    if (!value) throw new Error(`Missing Script Property: ${key}`);
    config[toCamel_(key)] = value;
  });
  config.syncDryRun = (props.getProperty("SYNC_DRY_RUN") || "true").toLowerCase() !== "false";
  return config;
}

function collectFiles_(folder, relativeFolder) {
  const output = [];
  const files = folder.getFiles();
  while (files.hasNext()) {
    const file = files.next();
    const relativePath = joinPath_(relativeFolder, file.getName());
    output.push({ file, relativePath });
  }

  const folders = folder.getFolders();
  while (folders.hasNext()) {
    const child = folders.next();
    output.push(...collectFiles_(child, joinPath_(relativeFolder, child.getName())));
  }
  return output;
}

function syncOneFile_(item, config) {
  const githubPath = joinPath_(config.githubTargetPrefix, item.relativePath);
  if (!isSupported_(item.file)) {
    return { status: "unsupported", githubPath };
  }

  const blob = item.file.getBlob();
  const bytes = blob.getBytes();
  const sha256 = hashBytes_(bytes);
  const stateKey = `sync:${item.file.getId()}:${githubPath}`;
  const props = PropertiesService.getScriptProperties();
  const previous = JSON.parse(props.getProperty(stateKey) || "null");

  if (previous && previous.sha256 === sha256) {
    return { status: "skipped", githubPath };
  }

  if (config.syncDryRun) {
    Logger.log(`[dry-run] would sync ${githubPath} (${sha256})`);
    return { status: previous ? "updated" : "created", githubPath };
  }

  const existing = fetchGitHubFile_(githubPath, config);
  const message = previous
    ? `Sync Drive update: ${githubPath}`
    : `Sync Drive file: ${githubPath}`;
  const payload = {
    message,
    content: Utilities.base64Encode(bytes),
    branch: config.githubBranch,
  };
  if (existing && existing.sha) payload.sha = existing.sha;

  const response = putGitHubFile_(githubPath, payload, config);
  props.setProperty(stateKey, JSON.stringify({
    sha256,
    driveModifiedTime: item.file.getLastUpdated().toISOString(),
    githubPath,
    lastCommitSha: response.commit && response.commit.sha,
  }));

  return { status: existing ? "updated" : "created", githubPath };
}

function fetchGitHubFile_(githubPath, config) {
  const url = githubContentsUrl_(githubPath, config) + `?ref=${encodeURIComponent(config.githubBranch)}`;
  const response = UrlFetchApp.fetch(url, {
    method: "get",
    headers: githubHeaders_(config),
    muteHttpExceptions: true,
  });
  if (response.getResponseCode() === 404) return null;
  if (response.getResponseCode() >= 300) {
    throw new Error(`GitHub fetch failed ${response.getResponseCode()}: ${response.getContentText()}`);
  }
  return JSON.parse(response.getContentText());
}

function putGitHubFile_(githubPath, payload, config) {
  const response = UrlFetchApp.fetch(githubContentsUrl_(githubPath, config), {
    method: "put",
    contentType: "application/json",
    headers: githubHeaders_(config),
    payload: JSON.stringify(payload),
    muteHttpExceptions: true,
  });
  if (response.getResponseCode() >= 300) {
    throw new Error(`GitHub write failed ${response.getResponseCode()}: ${response.getContentText()}`);
  }
  return JSON.parse(response.getContentText());
}

function githubContentsUrl_(githubPath, config) {
  return `https://api.github.com/repos/${config.githubOwner}/${config.githubRepo}/contents/${encodePath_(githubPath)}`;
}

function githubHeaders_(config) {
  return {
    Authorization: `Bearer ${config.githubToken}`,
    Accept: "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
  };
}

function isSupported_(file) {
  const name = file.getName().toLowerCase();
  return SUPPORTED_EXTENSIONS.some((extension) => name.endsWith(extension));
}

function hashBytes_(bytes) {
  const digest = Utilities.computeDigest(Utilities.DigestAlgorithm.SHA_256, bytes);
  return digest.map((byte) => {
    const value = (byte < 0 ? byte + 256 : byte).toString(16);
    return value.length === 1 ? `0${value}` : value;
  }).join("");
}

function joinPath_(left, right) {
  return [left, right].filter(Boolean).join("/").replace(/\/+ /g, "/");
}

function encodePath_(path) {
  return path.split("/").map(encodeURIComponent).join("/");
}

function toCamel_(key) {
  return key.toLowerCase().replace(/_([a-z])/g, (_, letter) => letter.toUpperCase());
}
