import { describe, expect, it } from "vitest";
import { buildQrImageUrl } from "./qr";

describe("event QR share", () => {
  it("requests a QR image for the exact public event URL", () => {
    const target = "https://example.test/event/anyang?plan=abc";
    const qr = buildQrImageUrl(target);
    expect(qr).toContain("api.qrserver.com/v1/create-qr-code");
    expect(decodeURIComponent(qr)).toContain(target);
  });
});
