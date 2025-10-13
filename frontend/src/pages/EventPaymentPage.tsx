import { useParams } from 'react-router-dom';
import EventCheckout from '@/components/EventCheckout';

/**
 * EventPaymentPage
 * Main page for browsing and purchasing premium events (£497-£2,997)
 * Uses direct Stripe Checkout for one-time payments (separate from subscriptions)
 */
const EventPaymentPage = () => {
  const { eventId } = useParams<{ eventId?: string }>();

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-white py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Page Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
            Premium M&A Events
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Exclusive masterclasses, executive workshops, and VIP deal summits. Learn from industry
            leaders and build your M&A empire.
          </p>
          <p className="text-sm text-gray-500 mt-4">
            💡 <strong>Community Leaders</strong> earn 20% revenue share on events they host
          </p>
        </div>

        {/* Event Checkout Component */}
        <EventCheckout defaultEventId={eventId} />

        {/* Additional Information */}
        <div className="mt-16 bg-blue-50 border border-blue-200 rounded-lg p-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-4 text-center">
            What's Included with Every Event
          </h2>
          <div className="grid md:grid-cols-3 gap-6 text-center">
            <div>
              <div className="text-4xl mb-2">🎥</div>
              <h3 className="font-semibold text-gray-900 mb-2">Live Interactive Session</h3>
              <p className="text-sm text-gray-600">
                Real-time engagement with industry leaders and fellow M&A professionals
              </p>
            </div>
            <div>
              <div className="text-4xl mb-2">📚</div>
              <h3 className="font-semibold text-gray-900 mb-2">Exclusive Resources</h3>
              <p className="text-sm text-gray-600">
                Downloadable templates, checklists, and frameworks you can implement immediately
              </p>
            </div>
            <div>
              <div className="text-4xl mb-2">🏆</div>
              <h3 className="font-semibold text-gray-900 mb-2">Certificate & Recording</h3>
              <p className="text-sm text-gray-600">
                Official completion certificate and 30-day access to session recording
              </p>
            </div>
          </div>
        </div>

        {/* Subscription Upsell */}
        <div className="mt-12 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg p-8 text-center text-white">
          <h2 className="text-2xl font-bold mb-4">Want Unlimited Event Access?</h2>
          <p className="text-lg mb-6 text-blue-100">
            <strong>Growth Firm</strong> and higher subscribers get access to all events, plus VIP
            networking and priority introductions.
          </p>
          <a
            href="/pricing"
            className="inline-block bg-white text-blue-600 font-semibold px-8 py-3 rounded-lg hover:bg-gray-100 transition-colors"
          >
            View Subscription Plans
          </a>
        </div>
      </div>
    </div>
  );
};

export default EventPaymentPage;
