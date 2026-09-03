const SPORTS_TICKER_EDITOR_STABILITY_VERSION = "0.1.0";

const applySportsTickerEditorStabilityPatch = () => {
  const EditorClass = customElements.get("sports-ticker-card-editor");
  if (!EditorClass || EditorClass.__sportsTickerStableHass) return Boolean(EditorClass);

  Object.defineProperty(EditorClass.prototype, "hass", {
    configurable: true,
    set(hass) {
      this._hass = hass;
      const signature = typeof this._availableSports === "function"
        ? this._availableSports().map(([key, sport]) => `${key}:${sport.entity}`).join("|")
        : "";

      const firstRender = !this.shadowRoot || !this.shadowRoot.childNodes.length;
      if (firstRender || signature !== this._sportsTickerAvailabilitySignature) {
        this._sportsTickerAvailabilitySignature = signature;
        this._render?.();
      }
    },
  });

  EditorClass.__sportsTickerStableHass = true;
  console.info(
    `%c SPORTS-TICKER-EDITOR-STABILITY %c v${SPORTS_TICKER_EDITOR_STABILITY_VERSION} `,
    "background:#444;color:#fff;font-weight:700",
    "background:#eee;color:#444",
  );
  return true;
};

if (!applySportsTickerEditorStabilityPatch()) {
  customElements.whenDefined("sports-ticker-card-editor").then(applySportsTickerEditorStabilityPatch);
}
