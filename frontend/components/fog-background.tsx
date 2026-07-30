export function FogBackground() {
  return (
    <div
      aria-hidden="true"
      className="pointer-events-none fixed inset-0 -z-10 overflow-hidden bg-background"
    >
      {/* subtle grain / vignette base */}
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_color-mix(in_oklch,var(--gold)_6%,transparent),transparent_55%)]" />

      {/* drifting warm + cool fog blobs */}
      <div className="animate-drift-a absolute -left-32 top-[-10%] h-[42rem] w-[42rem] rounded-full bg-[radial-gradient(circle,_color-mix(in_oklch,var(--gold)_38%,transparent),transparent_65%)] blur-3xl" />
      <div className="animate-drift-b absolute right-[-15%] top-1/4 h-[38rem] w-[38rem] rounded-full bg-[radial-gradient(circle,_color-mix(in_oklch,var(--foreground)_22%,transparent),transparent_65%)] blur-3xl" />
      <div className="animate-drift-c absolute bottom-[-10%] left-1/3 h-[40rem] w-[40rem] rounded-full bg-[radial-gradient(circle,_color-mix(in_oklch,var(--gold)_24%,transparent),transparent_65%)] blur-3xl" />

      {/* darken toward edges for depth */}
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,transparent_40%,var(--background)_100%)]" />
    </div>
  )
}
