'use client';

import { useRef, useState } from 'react';
import Link from 'next/link';

export default function DevocionaisCarousel({ data }: { data: any[] }) {
  const scrollRef = useRef<HTMLDivElement>(null);
  const [isMouseDown, setIsMouseDown] = useState(false);
  const [startX, setStartX] = useState(0);
  const [scrollLeft, setScrollLeft] = useState(0);
  const [isDragging, setIsDragging] = useState(false);

  // Grab-to-pan handlers
  const handleMouseDown = (e: React.MouseEvent) => {
    if (!scrollRef.current) return;
    setIsMouseDown(true);
    setIsDragging(false);
    setStartX(e.pageX - scrollRef.current.offsetLeft);
    setScrollLeft(scrollRef.current.scrollLeft);
  };

  const handleMouseLeave = () => {
    setIsMouseDown(false);
    setIsDragging(false);
  };
  
  const handleMouseUp = () => {
    setIsMouseDown(false);
    // Let onClick handle the actual click prevention if it was dragging. 
    // We clear isDragging shortly after to allow subsequent clicks.
    setTimeout(() => setIsDragging(false), 50);
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!isMouseDown || !scrollRef.current) return;
    
    const x = e.pageX - scrollRef.current.offsetLeft;
    const walk = (x - startX);
    
    if (Math.abs(walk) > 5) {
      setIsDragging(true);
      e.preventDefault();
      scrollRef.current.scrollLeft = scrollLeft - (walk * 2.5); // Smooth dragging acceleration
    }
  };

  const scrollByAmount = (amount: number) => {
    if (scrollRef.current) {
      scrollRef.current.scrollBy({ left: amount, behavior: 'smooth' });
    }
  };

  return (
    <div style={{ position: 'relative', width: '100%', maxWidth: '1000px', margin: '0 auto' }}>
      
      {/* Container de Rolagem */}
      <div 
        ref={scrollRef}
        onMouseDown={handleMouseDown}
        onMouseLeave={handleMouseLeave}
        onMouseUp={handleMouseUp}
        onMouseMove={handleMouseMove}
        style={{
          display: 'flex',
          gap: '1.2rem',
          overflowX: 'auto',
          padding: '1rem',
          paddingBottom: '1rem', // Reduzido já que os botões ficam embaixo
          cursor: isDragging ? 'grabbing' : 'grab',
          scrollbarWidth: 'none',
          msOverflowStyle: 'none',
          WebkitOverflowScrolling: 'touch',
          scrollSnapType: isDragging ? 'none' : 'x mandatory',
        }}
        className="hide-scrollbar"
      >
        {data.map((d: any, i: number) => (
          <Link
            key={i}
            href={`/culto-domestico/${d.nico_plano.semana}/${d.nico_plano.dia}`}
            className="glass"
            style={{
              display: 'flex',
              flexDirection: 'column',
              padding: '1.5rem',
              borderRadius: '16px',
              textDecoration: 'none',
              color: 'inherit',
              transition: 'transform 0.3s ease, box-shadow 0.3s ease',
              flex: '0 0 auto',
              width: '300px',
              scrollSnapAlign: 'center',
              background: 'var(--glass-bg)',
              border: '1px solid var(--glass-border)',
            }}
            onClick={(e) => {
              if (isDragging) {
                e.preventDefault();
              }
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
              <span style={{ fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.1em', color: 'var(--accent-gold)', fontWeight: 600 }}>
                Semana {d.nico_plano.semana} · Dia {d.nico_plano.dia}
              </span>
            </div>
            <h3 style={{ fontFamily: 'var(--font-serif)', fontSize: '1rem', marginBottom: '0.5rem' }}>
              {d.ref}
            </h3>
            <p style={{ 
              fontSize: '0.85rem', 
              color: 'var(--text-secondary)',
              display: '-webkit-box',
              WebkitLineClamp: 4,
              WebkitBoxOrient: 'vertical',
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              lineHeight: '1.5'
            }}>
              "{d.versiculo}"
            </p>
          </Link>
        ))}
      </div>

      {/* Controles do Carrossel (Elegantes e fora dos cards) */}
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center',
        gap: '1.5rem', 
        marginTop: '1rem',
        paddingBottom: '1rem'
      }}>
        <button 
          onClick={() => scrollByAmount(-320)}
          style={{
            background: 'var(--glass-bg)', backdropFilter: 'blur(8px)',
            border: '1px solid var(--glass-border)', color: 'var(--accent-gold)',
            width: '45px', height: '45px', borderRadius: '50%', cursor: 'pointer',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            boxShadow: '0 4px 15px rgba(0,0,0,0.2)', transition: 'all 0.2s',
            fontSize: '1.2rem'
          }}
          aria-label="Rolar para esquerda"
          onMouseOver={(e) => e.currentTarget.style.borderColor = 'var(--accent-gold)'}
          onMouseOut={(e) => e.currentTarget.style.borderColor = 'var(--glass-border)'}
        >
          &#8592;
        </button>
        <button 
          onClick={() => scrollByAmount(320)}
          style={{
            background: 'var(--glass-bg)', backdropFilter: 'blur(8px)',
            border: '1px solid var(--glass-border)', color: 'var(--accent-gold)',
            width: '45px', height: '45px', borderRadius: '50%', cursor: 'pointer',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            boxShadow: '0 4px 15px rgba(0,0,0,0.2)', transition: 'all 0.2s',
            fontSize: '1.2rem'
          }}
          aria-label="Rolar para direita"
          onMouseOver={(e) => e.currentTarget.style.borderColor = 'var(--accent-gold)'}
          onMouseOut={(e) => e.currentTarget.style.borderColor = 'var(--glass-border)'}
        >
          &#8594;
        </button>
      </div>
    </div>
  );
}
