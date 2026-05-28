export default function LogoMark({ size = 44, withWordmark = false, subtitle = 'Workflow Copilot' }) {
  return (
    <div className="nf-logo-lockup" style={{ '--nf-logo-size': `${size}px` }}>
      <svg
        className="nf-logo-mark"
        viewBox="0 0 64 64"
        aria-hidden="true"
        focusable="false"
      >
        <defs>
          <linearGradient id="nfLogoGradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#8fb6d9" />
            <stop offset="100%" stopColor="#2b6f9f" />
          </linearGradient>
        </defs>
        <rect x="4" y="4" width="56" height="56" rx="16" fill="#16212b" />
        <path
          d="M20 44V20h6l12 15V20h6v24h-6L26 29v15z"
          fill="url(#nfLogoGradient)"
        />
        <circle cx="18" cy="18" r="3" fill="#d8e7f3" />
        <circle cx="46" cy="18" r="3" fill="#d8e7f3" />
        <circle cx="46" cy="46" r="3" fill="#d8e7f3" />
      </svg>

      {withWordmark && (
        <div className="nf-logo-copy">
          <div className="nf-logo-wordmark">Workflow Copilot</div>
          <div className="nf-logo-subtitle">{subtitle}</div>
        </div>
      )}
    </div>
  )
}
