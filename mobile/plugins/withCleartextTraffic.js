const { withAndroidManifest } = require("@expo/config-plugins");

const LINK_SCHEMES = ["http", "https", "personal-agent", "granja-luna"];

function hasViewIntentForScheme(query, scheme) {
  return (query.intent ?? []).some(
    (intent) =>
      intent.action?.some(
        (action) => action.$?.["android:name"] === "android.intent.action.VIEW",
      ) &&
      intent.data?.some((data) => data.$?.["android:scheme"] === scheme),
  );
}

module.exports = function withCleartextTraffic(config) {
  return withAndroidManifest(config, (androidConfig) => {
    const manifest = androidConfig.modResults.manifest;
    const application = manifest.application?.[0];

    if (application) {
      application.$["android:usesCleartextTraffic"] = "true";
    }

    const queryBlocks = manifest.queries ?? [];
    let linkQueries = queryBlocks.find((query) =>
      (query.intent ?? []).some((intent) =>
        intent.action?.some(
          (action) => action.$?.["android:name"] === "android.intent.action.VIEW",
        ),
      ),
    );
    if (!linkQueries) {
      linkQueries = { intent: [] };
      queryBlocks.push(linkQueries);
    }

    for (const scheme of LINK_SCHEMES) {
      if (hasViewIntentForScheme(linkQueries, scheme)) continue;
      linkQueries.intent.push({
        action: [{ $: { "android:name": "android.intent.action.VIEW" } }],
        category: [{ $: { "android:name": "android.intent.category.BROWSABLE" } }],
        data: [{ $: { "android:scheme": scheme } }],
      });
    }
    manifest.queries = queryBlocks;

    return androidConfig;
  });
};
