import { useEffect } from 'react'

/**
 * AnalyticsListener wires global analytics hooks (e.g., GA, Mixpanel) after
 * Clerk authentication has initialised. Render deployment only needs the side
 * effects, so we keep the component lightweight and return null.
 */
const AnalyticsListener = () => {
  useEffect(() => {
    if (typeof window === 'undefined') return

    // ensure global analytics libraries exist before invoking
    if (window.gtag) {
      window.gtag('config', 'GA_MEASUREMENT_ID', { send_page_view: false })
    }

    if ((window as any).analytics?.init) {
      ;(window as any).analytics.init()
    }
  }, [])

  return null
}

export default AnalyticsListener
