'use client';

import { useState, useRef, useEffect } from 'react';
import { sendChatMessage } from '@/lib/api';
import { ChatMessage, CarRecommendation, ConstraintReport } from '@/types';
import CarCard from '@/components/CarCard';
import TextType from '@/components/TextType';
import Navbar from '@/components/Navbar';
import RippleGrid from '@/components/RippleGrid';
import ManualWeightInput from '@/components/ManualWeightInput';
import DisambiguationPopup from '@/components/DisambiguationPopup';
import api from '@/lib/api';
import styles from './page.module.css';
import { HiPaperAirplane } from 'react-icons/hi2';
import { RiRobot2Fill } from 'react-icons/ri';
import { HiUser } from 'react-icons/hi2';

const WELCOME_CONTENT = 'Halo! 👋 Saya **Otobot** — asisten rekomendasi mobil cerdas Anda.\n\nCeritakan kebutuhan dan budget Anda — saya akan merekomendasikan **5 kandidat mobil terbaik** yang sudah diranking secara objektif! 🚗';

function createWelcomeMessage(): ChatMessage {
  return {
    id: 'welcome',
    role: 'assistant',
    content: WELCOME_CONTENT,
    timestamp: new Date(),
  };
}

function parseMarkdown(text: string): string {
  return text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/\n/g, '<br/>');
}



function MsgBubble({ msg }: { msg: ChatMessage }) {
  const isUser = msg.role === 'user';
  return (
    <div className={`${styles.msgRow} ${isUser ? styles.msgRowUser : ''}`}>
      {!isUser && <div className={styles.avatarBot}><RiRobot2Fill size={14} /></div>}
      <div className={`${styles.bubble} ${isUser ? styles.bubbleUser : styles.bubbleBot}`}>
        <span dangerouslySetInnerHTML={{ __html: parseMarkdown(msg.content) }} />
        <span className={styles.timestamp}>
          {msg.timestamp.toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit' })}
        </span>
      </div>
      {isUser && <div className={styles.avatarUser}><HiUser size={14} /></div>}
    </div>
  );
}

function RankedCars({ cars, constraintReport }: { cars: CarRecommendation[], constraintReport?: ConstraintReport }) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className={styles.carsSection}>
      <div className={styles.carsSectionHeader}>
        <span className={styles.carsSectionTitle}>🏆 Top {cars.length} Rekomendasi</span>
      </div>

      <div className={styles.carGrid}>
        {cars.map((car, i) => (
          <div key={i} className={styles.carRow}>
            <CarCard car={car} rank={i + 1} expanded={expanded} onToggleExpand={() => setExpanded(!expanded)} />
          </div>
        ))}
      </div>
    </div>
  );
}

export default function ChatbotPage() {
  const [messages, setMessages] = useState<ChatMessage[]>(() => [createWelcomeMessage()]);
  const [savedWeights, setSavedWeights] = useState<Record<string, number> | null>(null);
  const [sessionId, setSessionId] = useState<string>(() => Date.now().toString());
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const submitWeights = async (weights: Record<string, number>, payload: Record<string, unknown>, msgId: string) => {
    setSavedWeights(weights);
    
    // Gabungkan semua pesan user sebagai user_message agar tergabung di history
    const fullConversation = messages.filter(m => m.role === 'user').map(m => m.content).join(" | ");
    const finalPayload = { 
      ...payload, 
      manual_weights: weights, 
      session_id: sessionId,
      user_message: fullConversation
    };
    
    setLoading(true);

    try {
      console.log("[FRONTEND] Mengirim bobot manual ke FastAPI", finalPayload);
      const { data } = await api.post('/chat', finalPayload);

      const recs = data.recommendations || [];
      const constraint_report = data.constraint_report || null;

      setMessages(prev => prev.map(m => m.id === msgId ? { ...m, ask_weights_payload: undefined } : m));

      setMessages(prev => [...prev, {
        id: `b-${Date.now()}`,
        role: 'assistant',
        content: `Sip! Berdasarkan bobot preferensi Anda, berikut hasilnya:`,
        recommendations: recs,
        constraint_report: constraint_report,
        timestamp: new Date(),
      }]);


    } catch (e) {
      setMessages(prev => [...prev, {
        id: `e-${Date.now()}`,
        role: 'assistant',
        content: '⚠️ Gagal memuat rekomendasi dengan bobot manual.',
        timestamp: new Date(),
      }]);
    } finally {
      setLoading(false);
    }
  };

  const sendMessage = async (overrideText?: string) => {
    const text = (overrideText ?? input).trim();
    if (!text || loading) return;
    const userMsg: ChatMessage = {
      id: `u-${Date.now()}`,
      role: 'user',
      content: text,
      timestamp: new Date(),
    };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      console.log("==================================================");
      console.log(`[FRONTEND UI] User menekan tombol kirim dengan isi pesan: "${text}"`);
      // 1. Send text to Rasa via API
      const rasaResponses = await sendChatMessage(text);

      // Rasa returns an array of messages: [{ recipient_id: "user", text: "...", custom: {...} }]
      interface RasaMessage {
        recipient_id?: string;
        text?: string;
        custom?: {
          action?: string;
          payload?: Record<string, unknown>;
          recommendations?: CarRecommendation[];
          constraint_report?: ConstraintReport;
        };
      }

      if (Array.isArray(rasaResponses) && rasaResponses.length > 0) {
        // Gabungkan semua balasan teks jika ada banyak text
        const textParts = rasaResponses
          .map((r: RasaMessage) => r.text)
          .filter(Boolean)
          .join('\n\n');

        // Cari balasan custom action jika disediakan oleh actions.py
        const actionResponse = rasaResponses.find((r: RasaMessage) => r.custom && (r.custom.action === "ask_weights" || r.custom.action === "search_cars" || r.custom.action === "disambiguate_car"));

        // Cari balasan custom recommendations jika disediakan oleh actions.py
        const recResponse = rasaResponses.find((r: RasaMessage) => r.custom && r.custom.recommendations);
        const recs = recResponse ? recResponse.custom.recommendations || [] : [];
        const constraint_report = recResponse ? recResponse.custom.constraint_report || null : null;

        if (actionResponse) {
          const actionType = actionResponse.custom.action;

          if (actionType === "ask_weights" || (actionType === "search_cars" && !savedWeights)) {
            setMessages(prev => [...prev, {
              id: `b-${Date.now()}`,
              role: 'assistant',
              content: textParts || 'Silakan atur bobot kriteria yang paling penting menurut Anda.',
              ask_weights_payload: actionResponse.custom.payload,
              timestamp: new Date(),
            }]);
          } else if (actionType === "search_cars" && savedWeights) {
            setMessages(prev => [...prev, {
              id: `b-${Date.now()}-loading`,
              role: 'assistant',
              content: textParts || 'Baik, kriteria pencarian sedang saya sesuaikan...',
              timestamp: new Date(),
            }]);

            const payload = actionResponse.custom.payload;
            const fullConversation = [...messages, userMsg].filter(m => m.role === 'user').map(m => m.content).join(" | ");
            const finalPayload = { 
              ...payload, 
              manual_weights: savedWeights, 
              session_id: sessionId,
              user_message: fullConversation 
            };

            try {
              const { data } = await api.post('/chat', finalPayload);
              setMessages(prev => [...prev, {
                id: `b-${Date.now()}-res`,
                role: 'assistant',
                content: 'Sip! Berdasarkan bobot preferensi yang sebelumnya tersimpan, berikut hasil penyesuaian rekomendasinya:',
                recommendations: data.recommendations || [],
                constraint_report: data.constraint_report || null,
                timestamp: new Date(),
              }]);

            } catch (e) {
              setMessages(prev => [...prev, {
                id: `e-${Date.now()}`,
                role: 'assistant',
                content: '⚠️ Gagal memuat rekomendasi otomatis.',
                timestamp: new Date(),
              }]);
            }
          } else if (actionType === "disambiguate_car") {
            setMessages(prev => [...prev, {
              id: `b-${Date.now()}`,
              role: 'assistant',
              content: textParts || 'Ada beberapa varian mobil yang cocok. Silakan pilih salah satu untuk mencari alternatifnya:',
              disambiguation_payload: {
                matches: actionResponse.custom.matches || [],
                query: actionResponse.custom.query || 'Mobil target'
              },
              timestamp: new Date(),
            }]);
          }
        } else {
          setMessages(prev => [...prev, {
            id: `b-${Date.now()}`,
            role: 'assistant',
            content: textParts || '...',
            recommendations: recs,
            constraint_report: constraint_report,
            timestamp: new Date(),
          }]);
        }
      } else {
        setMessages(prev => [...prev, {
          id: `b-${Date.now()}`,
          role: 'assistant',
          content: 'Maaf, saya tidak mengerti. Bisa diulangi?',
          timestamp: new Date(),
        }]);
      }

      // Refresh history


    } catch {
      setMessages(prev => [...prev, {
        id: `e-${Date.now()}`,
        role: 'assistant',
        content: '⚠️ Gagal menghubungi server NLP (Rasa). Pastikan backend di `localhost:5005` berjalan.',
        timestamp: new Date(),
      }]);
    } finally {
      setLoading(false);
    }
  };

  const handleResetSession = async () => {
    const WELCOME_FRESH = createWelcomeMessage();
    setMessages([WELCOME_FRESH]);
    setInput('');
    setSavedWeights(null);
    setSessionId(Date.now().toString());

    // Clear backend
    try {
      await sendChatMessage('/restart');
    } catch (e) {
      console.error('Failed to clear Rasa backend conversation state:', e);
    }
  };

  const submitDisambiguation = async (match: any, msgId: string) => {
    // Hilangkan payload agar popup tidak muncul lagi
    setMessages(prev => prev.map(m => m.id === msgId ? { ...m, disambiguation_payload: undefined } : m));
    
    const payload = `/ask_similar_car{"target_car": "${match.brand} ${match.model}"}`;
    await sendMessage(payload);
  };

  return (
    <>
      <Navbar onReset={handleResetSession} />
      <div className={styles.pageLayout}>
        {/* ── Main Chat Area ── */}
        <main className={styles.chatMain} style={{ position: 'relative', overflow: 'hidden' }}>

          {/* ── Ripple Grid Animation (Only for Chat Background) ── */}
          <div style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', zIndex: 0, opacity: 10, pointerEvents: 'none' }}>
            <RippleGrid
              enableRainbow={true}
              gridColor="#000000ff"
              rippleIntensity={0}
              gridSize={10}
              gridThickness={60}
              mouseInteraction={true}
              mouseInteractionRadius={10}
            />
          </div>

        {/* Messages */}
        <div className={styles.chatBody} style={{ position: 'relative', zIndex: 1 }}>
          {messages.map(msg => {
            const payload = msg.ask_weights_payload as any;
            return (
              <div key={msg.id}>
                <MsgBubble msg={msg} />

                {payload && (
                  <div style={{ marginBottom: '12px', background: 'var(--bg-secondary)', padding: '14px', borderRadius: '12px', border: '1px solid var(--border-color)', fontSize: '0.8rem' }}>
                    <div style={{ fontWeight: 800, marginBottom: '10px', color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <RiRobot2Fill size={16} style={{ color: '#4090F7' }} /> Otobot menangkap:
                    </div>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                      {payload.entities?.length > 0 && (
                        <div style={{ display: 'flex', alignItems: 'flex-start', gap: '8px' }}>
                          <span style={{ fontWeight: 700, width: '100px', color: 'var(--text-muted)' }}>Filter Syarat:</span>
                          <span style={{ color: '#4090F7', fontWeight: 600 }}>{payload.entities.join(", ")}</span>
                        </div>
                      )}
                      {(payload.min_budget || payload.max_budget) && (
                        <div style={{ display: 'flex', alignItems: 'flex-start', gap: '8px' }}>
                          <span style={{ fontWeight: 700, width: '100px', color: 'var(--text-muted)' }}>Batas Budget:</span>
                          <span style={{ color: '#00BB77', fontWeight: 700 }}>
                            {payload.min_budget ? `Rp ${(payload.min_budget / 1000000).toLocaleString('id-ID')} Jt` : 'Rp 0'}
                            {' - '}
                            {payload.max_budget ? `Rp ${(payload.max_budget / 1000000).toLocaleString('id-ID')} Jt` : 'Tak Terbatas'}
                          </span>
                        </div>
                      )}
                    </div>
                    <div style={{ marginTop: '14px', paddingTop: '10px', borderTop: '1px solid var(--border-color)', color: 'var(--text-secondary)', fontStyle: 'italic' }}>
                      Saya telah menyiapkan profil bobot rekomendasi awal berdasarkan profil spesifik Anda. Silakan putuskan di bawah ini 👇
                    </div>
                  </div>
                )}

                {payload && (
                  <ManualWeightInput
                    initialWeights={payload.base_weight_profile || {}}
                    onSubmit={(w) => submitWeights(w, payload, msg.id)}
                    disabled={loading}
                  />
                )}

                {msg.disambiguation_payload && (
                  <DisambiguationPopup 
                    matches={msg.disambiguation_payload.matches}
                    query={msg.disambiguation_payload.query}
                    onSelect={(match) => submitDisambiguation(match, msg.id)}
                  />
                )}

                {msg.recommendations && msg.recommendations.length > 0 && (
                  <RankedCars cars={msg.recommendations} constraintReport={msg.constraint_report} />
                )}
              </div>
            );
          })}
          {loading && (
            <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '180px', margin: '16px 0', opacity: 0.9 }}>
              <div style={{ padding: '16px 20px', borderRadius: '14px', background: 'var(--bg-secondary)', border: '1px solid var(--border-color)', display: 'inline-flex', alignItems: 'center', gap: '10px' }}>
                <RiRobot2Fill size={18} style={{ color: '#4090F7', animation: 'pulse 2s infinite' }} />
                <TextType
                  text={[
                    "Otobot sedang menganalisis kebutuhan Anda...",
                    "Sistem sedang menyaring kandidat mobil terbaik...",
                    "Menghitung bobot ranking VIKOR...",
                    "Sebentar lagi selesai..."
                  ]}
                  typingSpeed={30}
                  pauseDuration={2000}
                  showCursor
                  cursorCharacter="|"
                  deletingSpeed={30}
                  cursorBlinkDuration={0.5}
                  style={{
                    fontSize: '0.85rem',
                    color: 'var(--text-primary)',
                    fontWeight: 600,
                  }}
                />
              </div>
            </div>
          )}
          <div ref={bottomRef} />
        </div>

        {/* Input */}
        <div className={styles.inputArea} style={{ position: 'relative', zIndex: 1 }}>
          <div className={styles.inputRow}>
            <input
              className={styles.input}
              type="text"
              placeholder="Ceritakan kebutuhan atau preferensi dan budget mobil Anda..."
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && !e.shiftKey && sendMessage()}
              disabled={loading}
            />
            <button
              className={styles.sendBtn}
              onClick={() => sendMessage()}
              disabled={loading || !input.trim()}
              aria-label="Kirim"
            >
              {loading ? <span className={styles.spinner} /> : <HiPaperAirplane size={17} />}
            </button>
          </div>
          <p className={styles.inputHint}>
            Tekan <kbd>Enter</kbd> untuk mengirim • Bahasa Indonesia
          </p>
        </div>
        </main>
      </div>
    </>
  );
}
