'use client';

import { useState, useEffect } from 'react';
import { Star } from 'lucide-react';
import { createClient } from '@/utils/supabase/client';
import styles from './RatingStars.module.css';

interface Props {
  devocionalId: string;
  initialTotal: number;
  initialCount: number;
}

export default function RatingStars({ devocionalId, initialTotal, initialCount }: Props) {
  const [hovered, setHovered] = useState<number>(0);
  const [rated, setRated] = useState<number>(0);
  const [stats, setStats] = useState({ total: initialTotal, count: initialCount });
  const [hasVoted, setHasVoted] = useState(false);

  useEffect(() => {
    const previousVote = localStorage.getItem(`ryle_rated_${devocionalId}`);
    if (previousVote) {
      setHasVoted(true);
      setRated(parseInt(previousVote, 10));
    }
  }, [devocionalId]);

  const handleRate = async (stars: number) => {
    if (hasVoted) return;
    
    // UI Optimistic update
    setRated(stars);
    setHasVoted(true);
    setStats(prev => ({ total: prev.total + stars, count: prev.count + 1 }));
    localStorage.setItem(`ryle_rated_${devocionalId}`, stars.toString());

    // Send to Supabase
    const supabase = createClient();
    try {
      await supabase.rpc('increment_rating', { 
        p_devocional_id: devocionalId, 
        p_stars: stars 
      });
    } catch (err) {
      console.error('Failed to save rating', err);
    }
  };

  const currentAverage = stats.count > 0 ? (stats.total / stats.count).toFixed(1) : '0';

  return (
    <div className={styles.container}>
      <h3 className={styles.title}>Avalie este devocional</h3>
      <div 
        className={styles.stars}
        onMouseLeave={() => setHovered(0)}
      >
        {[1, 2, 3, 4, 5].map((star) => (
          <button
            key={star}
            className={styles.starBtn}
            onClick={() => handleRate(star)}
            onMouseEnter={() => !hasVoted && setHovered(star)}
            disabled={hasVoted}
            aria-label={`Avaliar com ${star} estrelas`}
          >
            <Star 
              size={28} 
              className={`${styles.starIcon} ${(hovered >= star || rated >= star) ? styles.filled : ''}`}
            />
          </button>
        ))}
      </div>
      
      {hasVoted ? (
        <span className={styles.thanks}>Obrigado por avaliar!</span>
      ) : (
        <span className={styles.stats}>
          {stats.count > 0 ? `${currentAverage} ★ (${stats.count} avaliações)` : 'Seja o primeiro a avaliar!'}
        </span>
      )}
    </div>
  );
}
