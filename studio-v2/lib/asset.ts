/**
 * Prefix for public assets (4K images etc).
 * Empty on Vercel/normal builds; set to the githack base for static-export preview.
 */
export const assetBase = process.env.NEXT_PUBLIC_ASSET_BASE ?? "";

export function asset(path: string): string {
  return `${assetBase}${path}`;
}
