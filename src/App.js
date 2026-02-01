import React, { useState, useCallback } from 'react';

// ============================================================================
// GAMEDAY HQ V4.1 - BROADCAST EDITION
// "Find Your Spot. Talk Your Trash."
// ============================================================================

const GamedayHQ = () => {
  // Core state
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [showOnboarding, setShowOnboarding] = useState(true);
  const [userMode, setUserMode] = useState(null);
  const [password, setPassword] = useState('');
  const [loginError, setLoginError] = useState('');
  const [activeTab, setActiveTab] = useState('watch');
  const [selectedSport, setSelectedSport] = useState('basketball');
  const [selectedVenue, setSelectedVenue] = useState(null);
  const [hoveredVenue, setHoveredVenue] = useState(null);
  const [expandedCard, setExpandedCard] = useState(null);
  const [flippedCards, setFlippedCards] = useState({});
  const [selectedGame, setSelectedGame] = useState(null);
  const [favoriteTeams, setFavoriteTeams] = useState(['Duke', 'Auburn']);
  const [showTrashTalk, setShowTrashTalk] = useState(null);
  
  // Info/tooltip state
  const [showTooltip, setShowTooltip] = useState(null);
  const [showGradeInfo, setShowGradeInfo] = useState(false);
  const [showLegend, setShowLegend] = useState(false);

  // ============================================================================
  // DESIGN TOKENS - Clean broadcast style (Green & Gold)
  // ============================================================================
  const theme = {
    bg: '#FFFFFF',
    bgSecondary: '#F7F7F8',
    bgCard: '#FFFFFF',
    text: '#1a1a1a',
    textSecondary: '#6b7280',
    textMuted: '#9ca3af',
    border: '#e5e7eb',
    accent: '#166534',        // Forest green
    accentAlt: '#eab308',     // Gold
    success: '#16a34a',
    warning: '#f59e0b',
    danger: '#ef4444',
    live: '#dc2626',
  };

  // ============================================================================
  // STAT DEFINITIONS
  // ============================================================================
  const statDefinitions = {
    apRank: { label: 'AP Rank', desc: 'Associated Press national ranking voted by sports journalists' },
    confRank: { label: 'Conference Rank', desc: 'Team ranking within their conference standings' },
    record: { label: 'Season Record', desc: 'Wins-Losses for the current season' },
    last5: { label: 'Last 5 Games', desc: 'Results of the 5 most recent games (W=Win, L=Loss)' },
    gradRate: { label: 'Graduation Rate', desc: 'NCAA Graduation Success Rate - % of athletes who graduate within 6 years' },
    avgTenure: { label: 'Avg Player Tenure', desc: 'Average years players stay at the school before transferring or going pro' },
    nilSpend: { label: 'NIL Budget', desc: 'Estimated annual Name, Image, Likeness spending in millions' },
    proPicks: { label: 'Pro Picks', desc: 'Total NBA/NFL draft picks in program history' },
    coachSalary: { label: 'Coach Salary', desc: 'Head coach annual compensation in millions' },
    spread: { label: 'Point Spread', desc: 'Expected margin of victory. Negative = favored, Positive = underdog' },
    moneyline: { label: 'Moneyline', desc: 'Odds to win outright. -150 means bet $150 to win $100' },
    overUnder: { label: 'Over/Under', desc: 'Projected total combined score. Bet whether actual is higher or lower' },
  };

  const pillarDefinitions = {
    winning: { name: 'Winning', icon: '🏆', color: '#c8102e', shortDesc: 'On-field success', fullDesc: 'Measures competitive success including win percentage, conference championships, tournament appearances, and national rankings.', factors: ['Win-loss record', 'Championships', 'Tournament success'] },
    development: { name: 'Player Development', icon: '⭐', color: '#3b82f6', shortDesc: 'Path to pros', fullDesc: 'Tracks how well the program develops players for professional careers. Based on draft picks relative to recruiting rankings.', factors: ['Pro draft picks', 'Development trajectory'] },
    education: { name: 'Education', icon: '🎓', color: '#10b981', shortDesc: 'Academic success', fullDesc: 'Academic outcomes for student-athletes including graduation rates. Uses NCAA Graduation Success Rate (GSR).', factors: ['Graduation rate', 'Academic eligibility'] },
    efficiency: { name: 'Efficiency', icon: '💰', color: '#f59e0b', shortDesc: 'Value for money', fullDesc: 'Results per dollar spent. Compares on-field results to NIL spending and program budget.', factors: ['Wins per NIL dollar', 'Budget efficiency'] }
  };

  // ============================================================================
  // DATA
  // ============================================================================
  const teamsData = {
    basketball: [
      { id: 101, name: 'Duke', nickname: 'Blue Devils', slogan: 'Go To Hell, Carolina!', color: '#003087', colorAlt: '#001A57', location: 'Durham, NC', enrollment: 17620, conference: 'ACC', apRank: 2, confRank: 1, record: '17-2', wins: 17, losses: 2, last5: 'WWWLW', coachName: 'Jon Scheyer', coachSalary: 9.7, nilSpend: 6.5, gradRate: 95, avgTenure: 2.1, proPicks: 68, trashTalkCount: 142, trashTalkHot: true, trashTalkComments: [
        { user: '@cfan2024', text: "Duke's grad rate carrying that grade HARD 📚", likes: 89 },
        { user: '@uncalum', text: 'Scheyer getting $10M for what exactly? 💀', likes: 234 },
        { user: '@bluedevil4life', text: '68 pro picks dont lie. Stay mad.', likes: 156 },
      ]},
      { id: 102, name: 'UNC', nickname: 'Tar Heels', slogan: 'Go Heels!', color: '#7BAFD4', colorAlt: '#13294B', location: 'Chapel Hill, NC', enrollment: 19897, conference: 'ACC', apRank: 14, confRank: 3, record: '14-6', wins: 14, losses: 6, last5: 'WLWWL', coachName: 'Hubert Davis', coachSalary: 4.2, nilSpend: 4.5, gradRate: 88, avgTenure: 2.6, proPicks: 58, trashTalkCount: 89, trashTalkHot: false, trashTalkComments: [{ user: '@heelyes', text: '6 titles > 5 titles. Simple math.', likes: 167 }]},
      { id: 103, name: 'Auburn', nickname: 'Tigers', slogan: 'War Eagle!', color: '#0C2340', colorAlt: '#F26522', location: 'Auburn, AL', enrollment: 24505, conference: 'SEC', apRank: 1, confRank: 1, record: '19-1', wins: 19, losses: 1, last5: 'WWWWW', coachName: 'Bruce Pearl', coachSalary: 4.8, nilSpend: 4.2, gradRate: 84, avgTenure: 2.4, proPicks: 15, trashTalkCount: 203, trashTalkHot: true, trashTalkComments: [{ user: '@wareagle', text: '#1 and it aint even close 🦅', likes: 445 }]},
      { id: 104, name: 'Alabama', nickname: 'Crimson Tide', slogan: 'Roll Tide!', color: '#9E1B32', colorAlt: '#828A8F', location: 'Tuscaloosa, AL', enrollment: 32400, conference: 'SEC', apRank: 4, confRank: 2, record: '16-3', wins: 16, losses: 3, last5: 'WWLWW', coachName: 'Nate Oats', coachSalary: 5.2, nilSpend: 5.8, gradRate: 81, avgTenure: 2.3, proPicks: 18, trashTalkCount: 156, trashTalkHot: true, trashTalkComments: []},
      { id: 105, name: 'Kansas', nickname: 'Jayhawks', slogan: 'Rock Chalk!', color: '#0051BA', colorAlt: '#E8000D', location: 'Lawrence, KS', enrollment: 23590, conference: 'Big 12', apRank: 11, confRank: 3, record: '14-5', wins: 14, losses: 5, last5: 'LWWLW', coachName: 'Bill Self', coachSalary: 5.5, nilSpend: 5.2, gradRate: 80, avgTenure: 2.2, proPicks: 65, trashTalkCount: 78, trashTalkHot: false, trashTalkComments: []},
      { id: 106, name: 'Iowa State', nickname: 'Cyclones', slogan: 'Go Cyclones!', color: '#C8102E', colorAlt: '#F1BE48', location: 'Ames, IA', enrollment: 27104, conference: 'Big 12', apRank: 3, confRank: 1, record: '17-2', wins: 17, losses: 2, last5: 'WWWWL', coachName: 'T.J. Otzelberger', coachSalary: 3.2, nilSpend: 2.1, gradRate: 85, avgTenure: 3.2, proPicks: 12, trashTalkCount: 67, trashTalkHot: false, trashTalkComments: []},
      { id: 107, name: 'Kentucky', nickname: 'Wildcats', slogan: 'Go Big Blue!', color: '#0033A0', colorAlt: '#FFFFFF', location: 'Lexington, KY', enrollment: 22227, conference: 'SEC', apRank: 12, confRank: 6, record: '14-5', wins: 14, losses: 5, last5: 'WLWLW', coachName: 'Mark Pope', coachSalary: 8.5, nilSpend: 7.2, gradRate: 74, avgTenure: 1.9, proPicks: 72, trashTalkCount: 234, trashTalkHot: true, trashTalkComments: []},
      { id: 108, name: 'UConn', nickname: 'Huskies', slogan: 'Bleed Blue!', color: '#002868', colorAlt: '#FFFFFF', location: 'Storrs, CT', enrollment: 19241, conference: 'Big East', apRank: 16, confRank: 2, record: '14-5', wins: 14, losses: 5, last5: 'WLWWW', coachName: 'Dan Hurley', coachSalary: 4.0, nilSpend: 3.0, gradRate: 92, avgTenure: 3.0, proPicks: 25, trashTalkCount: 189, trashTalkHot: true, trashTalkComments: []},
    ]
  };

  const gamesData = [
    { id: 1, team1: 'Duke', team2: 'UNC', sport: 'basketball', status: 'live', time: 'LIVE', quarter: '2nd Half', clock: '8:42', score1: 52, score2: 48, channel: 'ESPN', favorite: 'Duke', spread: 3.5, moneyline1: -165, moneyline2: 140, overUnder: 154.5, publicBetting: { team1: 72, team2: 28 }, predictions: [
      { question: 'Duke wins outright', yes: 68, no: 32 },
      { question: 'Duke covers -3.5', yes: 52, no: 48 },
    ]},
    { id: 2, team1: 'Auburn', team2: 'Alabama', sport: 'basketball', status: 'upcoming', time: '2:00 PM', channel: 'ESPN', favorite: 'Auburn', spread: 6.5, moneyline1: -280, moneyline2: 220, overUnder: 162, publicBetting: { team1: 65, team2: 35 }, predictions: [{ question: 'Auburn wins outright', yes: 78, no: 22 }]},
    { id: 3, team1: 'Kansas', team2: 'Iowa State', sport: 'basketball', status: 'upcoming', time: '4:00 PM', channel: 'CBS', favorite: 'Iowa State', spread: 2, moneyline1: 120, moneyline2: -140, overUnder: 148, publicBetting: { team1: 45, team2: 55 }, predictions: []},
    { id: 4, team1: 'UConn', team2: 'Kentucky', sport: 'basketball', status: 'upcoming', time: '6:30 PM', channel: 'FOX', favorite: 'UConn', spread: 4, moneyline1: -180, moneyline2: 155, overUnder: 156, publicBetting: { team1: 58, team2: 42 }, predictions: []},
  ];

  const venuesData = [
    { id: 1, name: "Pluckers Wing Bar", address: "2222 Rio Grande St", distance: 0.8, tvs: 24, position: { x: 35, y: 25 }, gamesShowing: [1, 2], specials: [{ text: '🍗 50¢ wings during ranked matchups!' }]},
    { id: 2, name: "Cover 3", address: "2700 W Anderson Ln", distance: 1.2, tvs: 32, position: { x: 55, y: 20 }, gamesShowing: [1, 2, 3, 4], specials: [{ text: '📺 Every game, every channel!' }]},
    { id: 3, name: "Black Sheep Lodge", address: "2108 S Lamar Blvd", distance: 1.5, tvs: 12, position: { x: 25, y: 55 }, gamesShowing: [1], specials: []},
    { id: 4, name: "Lavaca Street Bar", address: "405 Lavaca St", distance: 2.1, tvs: 18, position: { x: 65, y: 45 }, gamesShowing: [1, 2], specials: [{ text: '🥃 $6 whiskey for SEC games' }]},
    { id: 5, name: "Scholz Garten", address: "1607 San Jacinto Blvd", distance: 2.4, tvs: 8, position: { x: 70, y: 60 }, gamesShowing: [2], specials: [{ text: '🎉 Texas watch party!' }]},
    { id: 6, name: "Little Woodrow's", address: "1501 S Lamar Blvd", distance: 1.8, tvs: 14, position: { x: 45, y: 70 }, gamesShowing: [1, 3], specials: [{ text: '🍻 $4 domestics' }]},
  ];

  // ============================================================================
  // HELPERS
  // ============================================================================
  const currentTeams = teamsData[selectedSport] || [];
  const getTeamByName = (name) => currentTeams.find(t => t.name === name);

  const calculatePillarScores = useCallback((team) => {
    const maxPicks = Math.max(...currentTeams.map(t => t.proPicks || 0));
    const maxWins = Math.max(...currentTeams.map(t => t.wins));
    return {
      winning: Math.round((team.wins / maxWins) * 100),
      development: Math.round(((team.proPicks || 0) / maxPicks) * 100),
      education: team.gradRate,
      efficiency: team.nilSpend > 0 ? Math.round(Math.min(100, (team.wins / team.nilSpend) * 8)) : 50
    };
  }, [currentTeams]);

  const calculateGrade = useCallback((team) => {
    const scores = calculatePillarScores(team);
    const avg = (scores.winning + scores.development + scores.education + scores.efficiency) / 4;
    let grade = avg >= 90 ? 'A' : avg >= 85 ? 'A-' : avg >= 80 ? 'B+' : avg >= 75 ? 'B' : avg >= 70 ? 'B-' : avg >= 65 ? 'C+' : avg >= 60 ? 'C' : avg >= 55 ? 'C-' : avg >= 50 ? 'D' : 'F';
    return { grade, score: Math.round(avg), pillars: scores };
  }, [calculatePillarScores]);

  const getGradeColor = (g) => ({ 'A': '#10b981', 'A-': '#34d399', 'B+': '#84cc16', 'B': '#a3e635', 'B-': '#facc15', 'C+': '#fbbf24', 'C': '#f97316', 'C-': '#fb923c', 'D': '#ef4444', 'F': '#dc2626' }[g] || '#888');
  const toggleCardFlip = (id) => setFlippedCards(p => ({ ...p, [id]: !p[id] }));
  const toggleFavorite = (name) => setFavoriteTeams(p => p.includes(name) ? p.filter(t => t !== name) : [...p, name]);
  const isVenueHighlighted = (v) => v.gamesShowing.some(id => { const g = gamesData.find(x => x.id === id); return g && (favoriteTeams.includes(g.team1) || favoriteTeams.includes(g.team2)); });
  const hasLiveGame = (v) => v.gamesShowing.some(id => gamesData.find(g => g.id === id)?.status === 'live');

  const VALID_CODES = ['gameday', 'beta', 'demo', '2026', 'receipts', 'trashtalk'];
  const handleLogin = () => VALID_CODES.includes(password.toLowerCase()) ? (setIsAuthenticated(true), setLoginError('')) : setLoginError('Invalid code');

  // ============================================================================
  // STAT TOOLTIP COMPONENT
  // ============================================================================
  const StatWithTooltip = ({ statKey, value, unit = '', size = 'normal' }) => {
    const def = statDefinitions[statKey];
    const isActive = showTooltip === statKey;
    return (
      <div style={{ position: 'relative', display: 'inline-block' }} onClick={(e) => { e.stopPropagation(); setShowTooltip(isActive ? null : statKey); }}>
        <div style={{ cursor: 'pointer', padding: size === 'small' ? '2px 4px' : '4px 8px', borderRadius: '6px', background: isActive ? theme.bgSecondary : 'transparent' }}>
          <div style={{ fontSize: size === 'small' ? '11px' : '12px', color: theme.textMuted, marginBottom: '2px' }}>{def?.label || statKey} <span style={{ fontSize: '10px' }}>ⓘ</span></div>
          <div style={{ fontSize: size === 'small' ? '14px' : '18px', fontWeight: '700', color: theme.text }}>{value}{unit}</div>
        </div>
        {isActive && def && (
          <div style={{ position: 'absolute', bottom: '100%', left: '50%', transform: 'translateX(-50%)', marginBottom: '8px', padding: '12px 16px', background: '#1f2937', color: '#fff', borderRadius: '12px', fontSize: '13px', lineHeight: '1.5', width: '220px', boxShadow: '0 10px 40px rgba(0,0,0,0.2)', zIndex: 1000 }}>
            <div style={{ fontWeight: '700', marginBottom: '6px' }}>{def.label}</div>
            <div style={{ color: 'rgba(255,255,255,0.8)' }}>{def.desc}</div>
            <div style={{ position: 'absolute', bottom: '-6px', left: '50%', transform: 'translateX(-50%)', width: 0, height: 0, borderLeft: '6px solid transparent', borderRight: '6px solid transparent', borderTop: '6px solid #1f2937' }} />
          </div>
        )}
      </div>
    );
  };

  // ============================================================================
  // LOGIN SCREEN
  // ============================================================================
  if (!isAuthenticated) {
    return (
      <div style={{ fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif', background: theme.bg, minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '20px' }}>
        <div style={{ maxWidth: '380px', width: '100%', textAlign: 'center' }}>
          <div style={{ marginBottom: '32px' }}>
            <div style={{ width: '80px', height: '80px', borderRadius: '20px', background: `linear-gradient(135deg, ${theme.accent}, ${theme.accentAlt})`, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '36px', margin: '0 auto 16px', boxShadow: '0 8px 24px rgba(22,101,52,0.3)' }}>🏟️</div>
            <h1 style={{ margin: '0 0 4px', fontSize: '32px', fontWeight: '900', color: theme.text }}>Gameday HQ</h1>
            <p style={{ margin: 0, color: theme.accent, fontSize: '15px', fontWeight: '600', fontStyle: 'italic' }}>"Find Your Spot. Talk Your Trash."</p>
          </div>
          <div style={{ background: theme.bgSecondary, borderRadius: '16px', padding: '32px 24px' }}>
            <input type="password" placeholder="Enter access code" value={password} onChange={(e) => setPassword(e.target.value)} onKeyPress={(e) => e.key === 'Enter' && handleLogin()} style={{ width: '100%', padding: '16px', background: theme.bg, border: `2px solid ${theme.border}`, borderRadius: '12px', color: theme.text, fontSize: '16px', textAlign: 'center', marginBottom: '16px', boxSizing: 'border-box', outline: 'none' }} />
            {loginError && <div style={{ color: theme.danger, fontSize: '14px', marginBottom: '16px', padding: '12px', background: '#fef2f2', borderRadius: '8px' }}>{loginError} — Try: <strong>demo</strong></div>}
            <button onClick={handleLogin} style={{ width: '100%', padding: '16px', background: theme.accent, border: 'none', borderRadius: '12px', color: '#fff', fontSize: '16px', fontWeight: '700', cursor: 'pointer' }}>Let's Go →</button>
          </div>
          <div style={{ marginTop: '24px', fontSize: '12px', color: theme.textMuted }}>v4.1 • Broadcast Edition</div>
        </div>
      </div>
    );
  }

  // ============================================================================
  // ONBOARDING
  // ============================================================================
  if (showOnboarding && !userMode) {
    return (
      <div style={{ fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif', background: theme.bg, minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', color: theme.text, padding: '20px' }}>
        <div style={{ maxWidth: '440px', width: '100%' }}>
          <h1 style={{ fontSize: '28px', fontWeight: '800', marginBottom: '8px', textAlign: 'center' }}>How do you watch? 👀</h1>
          <p style={{ color: theme.textSecondary, fontSize: '15px', marginBottom: '32px', textAlign: 'center' }}>We'll customize your experience</p>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {[
              { id: 'diehard', icon: '🏈', title: 'Die-Hard Fan', desc: 'I never miss a game', color: theme.accent },
              { id: 'casual', icon: '📺', title: 'Casual Viewer', desc: 'Big games only', color: theme.accentAlt },
              { id: 'bettor', icon: '📈', title: 'Sharp / Bettor', desc: 'Finding edges', color: '#3b82f6' },
              { id: 'social', icon: '🍻', title: 'Social Watcher', desc: 'Here for the vibes', color: '#8b5cf6' },
            ].map(m => (
              <button key={m.id} onClick={() => { setUserMode(m.id); setShowOnboarding(false); }} style={{ display: 'flex', alignItems: 'center', gap: '16px', padding: '20px 24px', background: theme.bgSecondary, border: `1px solid ${theme.border}`, borderRadius: '16px', color: theme.text, cursor: 'pointer', textAlign: 'left' }}>
                <div style={{ width: '52px', height: '52px', borderRadius: '14px', background: m.color, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '26px' }}>{m.icon}</div>
                <div style={{ flex: 1 }}><div style={{ fontSize: '17px', fontWeight: '700' }}>{m.title}</div><div style={{ fontSize: '14px', color: theme.textSecondary }}>{m.desc}</div></div>
                <span style={{ color: theme.textMuted, fontSize: '20px' }}>→</span>
              </button>
            ))}
          </div>
          <button onClick={() => { setUserMode('explore'); setShowOnboarding(false); }} style={{ marginTop: '24px', padding: '16px', background: 'transparent', border: `1px solid ${theme.border}`, borderRadius: '12px', color: theme.textSecondary, fontSize: '15px', cursor: 'pointer', width: '100%' }}>Just exploring →</button>
        </div>
      </div>
    );
  }

  // ============================================================================
  // TEAM CARD COMPONENT (with flip)
  // ============================================================================
  const TeamCard = ({ team, game, compact = false }) => {
    if (!team) return null;
    const cardId = `card-${team.id}-${game?.id || 'solo'}`;
    const isFlipped = flippedCards[cardId];
    const gradeData = calculateGrade(team);
    const isFavorite = favoriteTeams.includes(team.name);
    const isFavored = game?.favorite === team.name;

    if (compact) {
      return (
        <div style={{ background: theme.bgCard, borderRadius: '12px', border: `1px solid ${theme.border}`, padding: '12px' }}>
          <div style={{ height: '3px', background: team.color, borderRadius: '2px', marginBottom: '10px' }} />
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '10px' }}>
            <div style={{ width: '40px', height: '40px', borderRadius: '10px', background: team.color, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '18px', fontWeight: '800', color: '#fff' }}>{team.name.charAt(0)}</div>
            <div style={{ flex: 1 }}>
              <div style={{ fontSize: '14px', fontWeight: '700', color: theme.text }}>{team.name}</div>
              <div style={{ fontSize: '11px', color: theme.textSecondary }}>#{team.apRank} • {team.record}</div>
            </div>
            <div onClick={() => setShowGradeInfo(true)} style={{ padding: '6px 10px', background: `${getGradeColor(gradeData.grade)}15`, borderRadius: '8px', cursor: 'pointer' }}>
              <div style={{ fontSize: '18px', fontWeight: '900', color: getGradeColor(gradeData.grade) }}>{gradeData.grade}</div>
            </div>
          </div>
          {game && (
            <div style={{ padding: '8px', background: isFavored ? '#f0fdf4' : '#fefce8', borderRadius: '8px', textAlign: 'center' }}>
              <span style={{ fontSize: '14px', fontWeight: '700', color: isFavored ? '#16a34a' : '#ca8a04' }}>
                {isFavored ? `Favored -${game.spread}` : `Underdog +${game.spread}`}
              </span>
            </div>
          )}
        </div>
      );
    }

    return (
      <div style={{ perspective: '1000px', width: '100%' }}>
        <div style={{ position: 'relative', width: '100%', minHeight: isFlipped ? '480px' : '360px', transition: 'transform 0.5s ease', transformStyle: 'preserve-3d', transform: isFlipped ? 'rotateY(180deg)' : 'rotateY(0deg)' }}>
          
          {/* FRONT */}
          <div style={{ backfaceVisibility: 'hidden', position: 'absolute', width: '100%', background: theme.bgCard, border: `1px solid ${theme.border}`, borderRadius: '16px', overflow: 'hidden', boxSizing: 'border-box' }}>
            <div style={{ height: '4px', background: team.color }} />
            <div style={{ padding: '16px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '12px' }}>
                <span style={{ padding: '4px 10px', background: theme.bgSecondary, borderRadius: '6px', fontSize: '12px', fontWeight: '600', color: theme.textSecondary }}>#{team.apRank} NATIONAL</span>
                <span style={{ padding: '4px 10px', background: `${team.color}20`, borderRadius: '6px', fontSize: '12px', fontWeight: '600', color: team.color }}>{team.conference}</span>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '14px', marginBottom: '16px' }}>
                <div style={{ width: '60px', height: '60px', borderRadius: '14px', background: team.color, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '26px', fontWeight: '900', color: '#fff', boxShadow: `0 4px 12px ${team.color}44` }}>{team.name.charAt(0)}</div>
                <div>
                  <div style={{ fontSize: '20px', fontWeight: '800', color: theme.text }}>{team.name} {isFavorite && '⭐'}</div>
                  <div style={{ fontSize: '12px', color: theme.textSecondary }}>{team.location}</div>
                </div>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '8px', padding: '12px', background: theme.bgSecondary, borderRadius: '12px', marginBottom: '12px' }}>
                <StatWithTooltip statKey="record" value={team.record} size="small" />
                <StatWithTooltip statKey="gradRate" value={team.gradRate} unit="%" size="small" />
                <StatWithTooltip statKey="nilSpend" value={`$${team.nilSpend}M`} size="small" />
                <StatWithTooltip statKey="proPicks" value={team.proPicks} size="small" />
              </div>

              {/* Last 5 */}
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
                <span style={{ fontSize: '12px', color: theme.textMuted }}>Last 5:</span>
                <div style={{ display: 'flex', gap: '4px' }}>
                  {team.last5.split('').map((r, i) => (
                    <span key={i} style={{ width: '24px', height: '24px', borderRadius: '6px', background: r === 'W' ? '#dcfce7' : '#fee2e2', color: r === 'W' ? '#16a34a' : '#dc2626', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '12px', fontWeight: '700' }}>{r}</span>
                  ))}
                </div>
              </div>

              {/* Grade + Trash Talk */}
              <div style={{ display: 'flex', gap: '12px', marginBottom: '12px' }}>
                <div onClick={() => setShowGradeInfo(true)} style={{ flex: 1, padding: '12px', background: `${getGradeColor(gradeData.grade)}15`, borderRadius: '12px', textAlign: 'center', cursor: 'pointer' }}>
                  <div style={{ fontSize: '28px', fontWeight: '900', color: getGradeColor(gradeData.grade) }}>{gradeData.grade}</div>
                  <div style={{ fontSize: '11px', color: theme.textMuted }}>Program Grade ⓘ</div>
                </div>
                <div onClick={() => setShowTrashTalk(team.id)} style={{ flex: 1, padding: '12px', background: team.trashTalkHot ? '#fef2f2' : theme.bgSecondary, border: team.trashTalkHot ? '1px solid #fecaca' : `1px solid ${theme.border}`, borderRadius: '12px', textAlign: 'center', cursor: 'pointer' }}>
                  <div style={{ fontSize: '20px', fontWeight: '700', color: theme.text }}>💬 {team.trashTalkCount}</div>
                  <div style={{ fontSize: '11px', color: team.trashTalkHot ? theme.danger : theme.textMuted }}>{team.trashTalkHot ? '🔥 Trending' : 'Trash Talk'}</div>
                </div>
              </div>

              <button onClick={() => toggleCardFlip(cardId)} style={{ width: '100%', padding: '12px', background: theme.bgSecondary, border: `1px solid ${theme.border}`, borderRadius: '10px', color: theme.text, fontSize: '13px', fontWeight: '600', cursor: 'pointer' }}>
                ↻ Flip for Full Intel
              </button>
            </div>
          </div>

          {/* BACK */}
          <div style={{ backfaceVisibility: 'hidden', transform: 'rotateY(180deg)', position: 'absolute', top: 0, left: 0, width: '100%', background: theme.bgCard, border: `1px solid ${theme.border}`, borderRadius: '16px', overflow: 'hidden', boxSizing: 'border-box' }}>
            <div style={{ height: '4px', background: team.color }} />
            <div style={{ padding: '16px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                <button onClick={() => toggleCardFlip(cardId)} style={{ padding: '8px 12px', background: theme.bgSecondary, border: 'none', borderRadius: '8px', color: theme.text, fontSize: '13px', fontWeight: '600', cursor: 'pointer' }}>← Back</button>
                <span style={{ fontSize: '14px', fontWeight: '700', color: team.color }}>{team.name} Intel</span>
              </div>

              {/* Pillar breakdown */}
              <div style={{ marginBottom: '16px' }}>
                <div style={{ fontSize: '14px', fontWeight: '700', marginBottom: '12px', color: theme.text }}>Grade Breakdown</div>
                {Object.entries(pillarDefinitions).map(([key, pillar]) => (
                  <div key={key} style={{ marginBottom: '10px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
                      <span style={{ fontSize: '13px', color: theme.textSecondary }}>{pillar.icon} {pillar.name}</span>
                      <span style={{ fontSize: '14px', fontWeight: '700', color: pillar.color }}>{gradeData.pillars[key]}</span>
                    </div>
                    <div style={{ height: '6px', background: theme.bgSecondary, borderRadius: '3px', overflow: 'hidden' }}>
                      <div style={{ width: `${gradeData.pillars[key]}%`, height: '100%', background: pillar.color, borderRadius: '3px' }} />
                    </div>
                  </div>
                ))}
              </div>

              {/* Coach info */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginBottom: '16px' }}>
                <div style={{ padding: '12px', background: theme.bgSecondary, borderRadius: '10px' }}>
                  <div style={{ fontSize: '11px', color: theme.textMuted }}>Head Coach</div>
                  <div style={{ fontSize: '14px', fontWeight: '600', color: theme.text }}>{team.coachName}</div>
                  <div style={{ fontSize: '12px', color: theme.success }}>${team.coachSalary}M/yr</div>
                </div>
                <div style={{ padding: '12px', background: theme.bgSecondary, borderRadius: '10px' }}>
                  <StatWithTooltip statKey="avgTenure" value={team.avgTenure} unit=" yrs" size="small" />
                </div>
              </div>

              {/* Actions */}
              <div style={{ display: 'flex', gap: '8px' }}>
                <button onClick={() => toggleFavorite(team.name)} style={{ flex: 1, padding: '12px', background: isFavorite ? '#fef9c3' : theme.bgSecondary, border: isFavorite ? `1px solid ${theme.accentAlt}` : `1px solid ${theme.border}`, borderRadius: '10px', color: theme.text, fontSize: '13px', fontWeight: '600', cursor: 'pointer' }}>
                  {isFavorite ? '⭐ Saved' : '☆ Save'}
                </button>
                <button onClick={() => setShowTrashTalk(team.id)} style={{ flex: 1, padding: '12px', background: theme.bgSecondary, border: `1px solid ${theme.border}`, borderRadius: '10px', color: theme.text, fontSize: '13px', fontWeight: '600', cursor: 'pointer' }}>
                  💬 Talk Trash
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  };

  // ============================================================================
  // GAME CARD COMPONENT
  // ============================================================================
  const GameCard = ({ game }) => {
    const t1 = getTeamByName(game.team1);
    const t2 = getTeamByName(game.team2);
    const isLive = game.status === 'live';

    return (
      <div style={{ background: theme.bgCard, borderRadius: '16px', border: `1px solid ${theme.border}`, overflow: 'hidden' }}>
        <div style={{ padding: '12px 16px', background: isLive ? '#fef2f2' : theme.bgSecondary, borderBottom: `1px solid ${theme.border}`, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            {isLive ? (
              <span style={{ display: 'flex', alignItems: 'center', gap: '6px', padding: '4px 10px', background: theme.live, borderRadius: '6px', fontSize: '12px', fontWeight: '700', color: '#fff' }}>
                <span style={{ width: '6px', height: '6px', borderRadius: '50%', background: '#fff', animation: 'pulse 1s infinite' }} /> LIVE
              </span>
            ) : (
              <span style={{ fontSize: '14px', fontWeight: '600', color: theme.text }}>{game.time}</span>
            )}
            <span style={{ fontSize: '13px', color: theme.textSecondary }}>{game.channel}</span>
          </div>
          {isLive && <span style={{ fontSize: '13px', color: theme.textSecondary }}>{game.quarter} • {game.clock}</span>}
        </div>

        <div style={{ padding: '20px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div style={{ flex: 1, textAlign: 'center' }}>
              <div style={{ width: '56px', height: '56px', borderRadius: '14px', background: t1?.color || '#888', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '24px', fontWeight: '800', color: '#fff', margin: '0 auto 8px', border: favoriteTeams.includes(game.team1) ? `3px solid ${theme.accentAlt}` : 'none' }}>{game.team1.charAt(0)}</div>
              <div style={{ fontSize: '16px', fontWeight: '700', color: theme.text }}>{game.team1}</div>
              <div style={{ fontSize: '12px', color: theme.textMuted }}>#{t1?.apRank}</div>
              {isLive && <div style={{ fontSize: '28px', fontWeight: '900', color: theme.text, marginTop: '8px' }}>{game.score1}</div>}
            </div>
            <div style={{ padding: '0 16px', textAlign: 'center' }}>
              {isLive ? <div style={{ fontSize: '14px', color: theme.textMuted }}>—</div> : (
                <>
                  <div style={{ fontSize: '11px', color: theme.textMuted, marginBottom: '4px' }}>VS</div>
                  <div style={{ padding: '6px 12px', background: '#fef9c3', borderRadius: '8px', fontSize: '13px', fontWeight: '700', color: '#854d0e' }}>{game.favorite} -{game.spread}</div>
                </>
              )}
            </div>
            <div style={{ flex: 1, textAlign: 'center' }}>
              <div style={{ width: '56px', height: '56px', borderRadius: '14px', background: t2?.color || '#888', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '24px', fontWeight: '800', color: '#fff', margin: '0 auto 8px', border: favoriteTeams.includes(game.team2) ? `3px solid ${theme.accentAlt}` : 'none' }}>{game.team2.charAt(0)}</div>
              <div style={{ fontSize: '16px', fontWeight: '700', color: theme.text }}>{game.team2}</div>
              <div style={{ fontSize: '12px', color: theme.textMuted }}>#{t2?.apRank}</div>
              {isLive && <div style={{ fontSize: '28px', fontWeight: '900', color: theme.text, marginTop: '8px' }}>{game.score2}</div>}
            </div>
          </div>

          <div style={{ marginTop: '16px', padding: '12px', background: theme.bgSecondary, borderRadius: '10px', display: 'flex', justifyContent: 'space-around' }}>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '11px', color: theme.textMuted, marginBottom: '2px' }}>Public Bets</div>
              <div style={{ fontSize: '12px', fontWeight: '700' }}>
                <span style={{ color: game.publicBetting.team1 > 50 ? '#16a34a' : theme.text }}>{game.publicBetting.team1}%</span>
                <span style={{ color: theme.textMuted, margin: '0 4px' }}>-</span>
                <span style={{ color: game.publicBetting.team2 > 50 ? '#16a34a' : theme.text }}>{game.publicBetting.team2}%</span>
              </div>
            </div>
            <StatWithTooltip statKey="overUnder" value={game.overUnder} size="small" />
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '11px', color: theme.textMuted, marginBottom: '2px' }}>Moneyline</div>
              <div style={{ fontSize: '12px' }}>
                <span style={{ color: game.moneyline1 < 0 ? '#16a34a' : '#dc2626', fontWeight: '700' }}>{game.moneyline1 > 0 ? '+' : ''}{game.moneyline1}</span>
                <span style={{ color: theme.textMuted, margin: '0 4px' }}>/</span>
                <span style={{ color: game.moneyline2 < 0 ? '#16a34a' : '#dc2626', fontWeight: '700' }}>{game.moneyline2 > 0 ? '+' : ''}{game.moneyline2}</span>
              </div>
            </div>
          </div>

          <button onClick={() => setSelectedGame(game)} style={{ width: '100%', marginTop: '12px', padding: '12px', background: theme.accent, border: 'none', borderRadius: '10px', color: '#fff', fontSize: '14px', fontWeight: '700', cursor: 'pointer' }}>
            View Full Cards
          </button>
        </div>
      </div>
    );
  };

  // ============================================================================
  // MAIN APP
  // ============================================================================
  return (
    <div style={{ fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif', background: theme.bgSecondary, minHeight: '100vh', color: theme.text, maxWidth: '500px', margin: '0 auto' }} onClick={() => setShowTooltip(null)}>
      
      {/* HEADER */}
      <header style={{ position: 'sticky', top: 0, zIndex: 100, background: theme.bg, borderBottom: `1px solid ${theme.border}`, padding: '12px 16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <div style={{ width: '36px', height: '36px', borderRadius: '10px', background: `linear-gradient(135deg, ${theme.accent}, ${theme.accentAlt})`, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '18px' }}>🏟️</div>
            <div>
              <div style={{ fontSize: '16px', fontWeight: '800', color: theme.text }}>Gameday HQ</div>
              <div style={{ fontSize: '10px', color: theme.accent, fontStyle: 'italic' }}>Find Your Spot. Talk Your Trash.</div>
            </div>
          </div>
          <button onClick={() => setShowLegend(true)} style={{ padding: '8px 12px', background: theme.bgSecondary, border: `1px solid ${theme.border}`, borderRadius: '8px', fontSize: '12px', fontWeight: '600', color: theme.textSecondary, cursor: 'pointer' }}>📖 Legend</button>
        </div>
        <div style={{ display: 'flex', gap: '8px', background: theme.bgSecondary, borderRadius: '10px', padding: '4px' }}>
          {[{ id: 'basketball', icon: '🏀', label: 'Basketball' }, { id: 'football', icon: '🏈', label: 'Football' }].map(s => (
            <button key={s.id} onClick={() => setSelectedSport(s.id)} style={{ flex: 1, padding: '10px', background: selectedSport === s.id ? theme.bg : 'transparent', border: 'none', borderRadius: '8px', color: selectedSport === s.id ? theme.text : theme.textSecondary, fontSize: '13px', fontWeight: '600', cursor: 'pointer', boxShadow: selectedSport === s.id ? '0 1px 3px rgba(0,0,0,0.1)' : 'none' }}>{s.icon} {s.label}</button>
          ))}
        </div>
      </header>

      {/* MAIN CONTENT */}
      <main style={{ padding: '16px', paddingBottom: '100px' }}>
        
        {/* WATCH TAB - Map */}
        {activeTab === 'watch' && (
          <div>
            {/* Favorite Teams */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px', overflowX: 'auto', paddingBottom: '4px' }}>
              <span style={{ fontSize: '12px', color: theme.textMuted, flexShrink: 0 }}>YOUR TEAMS:</span>
              {favoriteTeams.length === 0 ? <span style={{ fontSize: '12px', color: theme.textMuted }}>None saved</span> : favoriteTeams.map(n => {
                const t = getTeamByName(n);
                return t ? (
                  <div key={n} style={{ display: 'flex', alignItems: 'center', gap: '6px', padding: '6px 12px', background: `${t.color}15`, border: `1px solid ${t.color}`, borderRadius: '10px', flexShrink: 0 }}>
                    <span style={{ width: '20px', height: '20px', borderRadius: '6px', background: t.color, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '10px', fontWeight: '800', color: '#fff' }}>{t.name.charAt(0)}</span>
                    <span style={{ fontSize: '12px', fontWeight: '600', color: theme.text }}>{t.name}</span>
                    <button onClick={() => toggleFavorite(n)} style={{ background: 'none', border: 'none', color: theme.textMuted, cursor: 'pointer', padding: 0, fontSize: '14px' }}>×</button>
                  </div>
                ) : null;
              })}
            </div>

            {/* Map */}
            <div style={{ position: 'relative', height: '260px', background: theme.bg, borderRadius: '16px', border: `1px solid ${theme.border}`, overflow: 'hidden', marginBottom: '16px' }}>
              <div style={{ position: 'absolute', inset: 0, backgroundImage: `linear-gradient(${theme.border} 1px, transparent 1px), linear-gradient(90deg, ${theme.border} 1px, transparent 1px)`, backgroundSize: '40px 40px' }} />
              <div style={{ position: 'absolute', top: '12px', left: '12px', padding: '8px 14px', background: theme.bg, borderRadius: '10px', fontSize: '12px', fontWeight: '600', color: theme.text, boxShadow: '0 2px 8px rgba(0,0,0,0.1)', zIndex: 50 }}>📍 Austin, TX • {venuesData.length} venues</div>
              {venuesData.map(v => {
                const hl = isVenueHighlighted(v), lv = hasLiveGame(v), hv = hoveredVenue === v.id;
                return (
                  <div key={v.id} onClick={() => setSelectedVenue(v)} onMouseEnter={() => setHoveredVenue(v.id)} onMouseLeave={() => setHoveredVenue(null)} style={{ position: 'absolute', left: `${v.position.x}%`, top: `${v.position.y}%`, transform: 'translate(-50%, -50%)', cursor: 'pointer', transition: 'all 0.3s', opacity: hl || favoriteTeams.length === 0 ? 1 : 0.35, zIndex: hv ? 100 : hl ? 50 : 10 }}>
                    <div style={{ width: hv ? '52px' : '42px', height: hv ? '52px' : '42px', borderRadius: '14px', background: lv ? theme.live : hl ? theme.success : '#3b82f6', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: hv ? '22px' : '18px', boxShadow: hl ? '0 6px 20px rgba(16,185,129,0.4)' : lv ? '0 6px 20px rgba(220,38,38,0.4)' : '0 4px 12px rgba(0,0,0,0.15)', border: hl ? '3px solid #10b981' : '2px solid #fff', position: 'relative' }}>
                      🍺
                      {lv && <div style={{ position: 'absolute', top: '-4px', right: '-4px', width: '12px', height: '12px', borderRadius: '50%', background: theme.live, border: '2px solid #fff' }} />}
                      {v.gamesShowing.length > 0 && <div style={{ position: 'absolute', bottom: '-4px', right: '-4px', padding: '2px 5px', borderRadius: '6px', background: theme.text, color: '#fff', fontSize: '9px', fontWeight: '800' }}>{v.gamesShowing.length}</div>}
                    </div>
                    {hv && <div style={{ position: 'absolute', top: '100%', left: '50%', transform: 'translateX(-50%)', marginTop: '8px', padding: '8px 12px', background: theme.text, color: '#fff', borderRadius: '8px', whiteSpace: 'nowrap', fontSize: '12px', fontWeight: '600' }}>{v.name}<div style={{ fontSize: '10px', color: 'rgba(255,255,255,0.7)' }}>{v.distance} mi • {v.tvs} TVs</div></div>}
                  </div>
                );
              })}
            </div>

            {/* Venue List */}
            {!selectedVenue ? (
              <div>
                <h2 style={{ margin: '0 0 12px', fontSize: '16px', fontWeight: '700', color: theme.text }}>📍 Nearby Venues</h2>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                  {venuesData.sort((a, b) => { const ah = isVenueHighlighted(a), bh = isVenueHighlighted(b); if (ah && !bh) return -1; if (!ah && bh) return 1; return a.distance - b.distance; }).map(v => {
                    const hl = isVenueHighlighted(v), lv = hasLiveGame(v);
                    return (
                      <div key={v.id} onClick={() => setSelectedVenue(v)} style={{ background: theme.bgCard, border: `1px solid ${hl ? '#86efac' : theme.border}`, borderRadius: '14px', padding: '14px 16px', cursor: 'pointer', opacity: hl || favoriteTeams.length === 0 ? 1 : 0.6 }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                          <div>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                              <span style={{ fontSize: '15px', fontWeight: '700', color: theme.text }}>🍺 {v.name}</span>
                              {lv && <span style={{ padding: '3px 8px', background: theme.live, borderRadius: '6px', fontSize: '10px', fontWeight: '700', color: '#fff' }}>LIVE</span>}
                              {hl && <span style={{ fontSize: '12px' }}>⭐</span>}
                            </div>
                            <div style={{ fontSize: '12px', color: theme.textSecondary }}>{v.distance} mi • {v.tvs} TVs • {v.gamesShowing.length} games</div>
                          </div>
                          <span style={{ fontSize: '18px', color: theme.textMuted }}>→</span>
                        </div>
                        {v.specials.length > 0 && <div style={{ marginTop: '10px', padding: '8px 12px', background: '#fef9c3', borderRadius: '8px', fontSize: '12px', color: '#854d0e' }}>{v.specials[0].text}</div>}
                      </div>
                    );
                  })}
                </div>
              </div>
            ) : (
              <div style={{ background: theme.bgCard, border: `1px solid ${theme.border}`, borderRadius: '16px', padding: '20px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '16px' }}>
                  <div>
                    <div style={{ fontSize: '20px', fontWeight: '800', color: theme.text, marginBottom: '4px' }}>🍺 {selectedVenue.name}</div>
                    <div style={{ fontSize: '13px', color: theme.textSecondary }}>{selectedVenue.address} • {selectedVenue.distance} mi • {selectedVenue.tvs} TVs</div>
                  </div>
                  <button onClick={() => setSelectedVenue(null)} style={{ width: '36px', height: '36px', borderRadius: '10px', background: theme.bgSecondary, border: 'none', color: theme.text, fontSize: '18px', cursor: 'pointer' }}>×</button>
                </div>
                {selectedVenue.specials.length > 0 && (
                  <div style={{ background: '#fef9c3', border: `1px solid ${theme.accentAlt}`, borderRadius: '12px', padding: '14px', marginBottom: '16px' }}>
                    <div style={{ fontSize: '12px', fontWeight: '700', color: '#854d0e', marginBottom: '6px' }}>🎉 TODAY'S SPECIALS</div>
                    {selectedVenue.specials.map((s, i) => <div key={i} style={{ fontSize: '14px', color: '#713f12' }}>{s.text}</div>)}
                  </div>
                )}
                <div style={{ fontSize: '14px', fontWeight: '700', color: theme.text, marginBottom: '12px' }}>📺 Games at this venue</div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                  {selectedVenue.gamesShowing.map(id => {
                    const g = gamesData.find(x => x.id === id);
                    if (!g) return null;
                    const t1 = getTeamByName(g.team1), t2 = getTeamByName(g.team2);
                    return (
                      <div key={id} onClick={() => setSelectedGame(g)} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '12px', background: theme.bgSecondary, borderRadius: '10px', cursor: 'pointer' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                          <div style={{ width: '32px', height: '32px', borderRadius: '8px', background: t1?.color, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '14px', fontWeight: '800', color: '#fff' }}>{g.team1.charAt(0)}</div>
                          <span style={{ fontSize: '13px', color: theme.textMuted }}>vs</span>
                          <div style={{ width: '32px', height: '32px', borderRadius: '8px', background: t2?.color, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '14px', fontWeight: '800', color: '#fff' }}>{g.team2.charAt(0)}</div>
                        </div>
                        <div style={{ textAlign: 'right' }}>
                          {g.status === 'live' ? (
                            <span style={{ padding: '4px 8px', background: theme.live, borderRadius: '6px', fontSize: '11px', fontWeight: '700', color: '#fff' }}>LIVE {g.score1}-{g.score2}</span>
                          ) : (
                            <span style={{ fontSize: '13px', fontWeight: '600', color: theme.text }}>{g.time}</span>
                          )}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}
          </div>
        )}

        {/* GAMES TAB */}
        {activeTab === 'games' && (
          <div>
            <h2 style={{ margin: '0 0 16px', fontSize: '18px', fontWeight: '800', color: theme.text }}>Today's Games</h2>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              {gamesData.filter(g => g.sport === selectedSport).map(g => <GameCard key={g.id} game={g} />)}
            </div>
          </div>
        )}

        {/* TEAMS TAB */}
        {activeTab === 'teams' && (
          <div>
            <h2 style={{ margin: '0 0 16px', fontSize: '18px', fontWeight: '800', color: theme.text }}>All Teams</h2>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              {currentTeams.sort((a, b) => (a.apRank || 999) - (b.apRank || 999)).map(t => <TeamCard key={t.id} team={t} />)}
            </div>
          </div>
        )}

        {/* SAVED TAB */}
        {activeTab === 'saved' && (
          <div>
            <h2 style={{ margin: '0 0 16px', fontSize: '18px', fontWeight: '800', color: theme.text }}>Saved Teams</h2>
            {favoriteTeams.length === 0 ? (
              <div style={{ textAlign: 'center', padding: '48px 24px', background: theme.bg, borderRadius: '16px', border: `2px dashed ${theme.border}` }}>
                <div style={{ fontSize: '40px', marginBottom: '12px' }}>⭐</div>
                <div style={{ fontSize: '16px', fontWeight: '600', color: theme.text, marginBottom: '4px' }}>No saved teams yet</div>
                <div style={{ fontSize: '14px', color: theme.textSecondary }}>Flip any team card and tap "Save" to add it here</div>
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                {favoriteTeams.map(name => { const t = getTeamByName(name); return t ? <TeamCard key={t.id} team={t} /> : null; })}
              </div>
            )}
          </div>
        )}
      </main>

      {/* BOTTOM NAV */}
      <nav style={{ position: 'fixed', bottom: 0, left: '50%', transform: 'translateX(-50%)', width: '100%', maxWidth: '500px', background: theme.bg, borderTop: `1px solid ${theme.border}`, display: 'flex', justifyContent: 'space-around', padding: '8px 0 24px', zIndex: 100 }}>
        {[
          { id: 'watch', icon: '📍', label: 'Watch' },
          { id: 'games', icon: '📺', label: 'Games' },
          { id: 'teams', icon: '🏀', label: 'Teams' },
          { id: 'saved', icon: '⭐', label: 'Saved' },
        ].map(t => (
          <button key={t.id} onClick={() => setActiveTab(t.id)} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '4px', padding: '8px 20px', background: activeTab === t.id ? `${theme.accent}15` : 'transparent', border: 'none', borderRadius: '12px', color: activeTab === t.id ? theme.accent : theme.textMuted, cursor: 'pointer' }}>
            <span style={{ fontSize: '22px' }}>{t.icon}</span>
            <span style={{ fontSize: '11px', fontWeight: '600' }}>{t.label}</span>
          </button>
        ))}
      </nav>

      {/* TRASH TALK MODAL */}
      {showTrashTalk && (() => {
        const team = currentTeams.find(t => t.id === showTrashTalk);
        if (!team) return null;
        return (
          <div onClick={() => setShowTrashTalk(null)} style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)', zIndex: 200, display: 'flex', alignItems: 'flex-end', justifyContent: 'center' }}>
            <div onClick={e => e.stopPropagation()} style={{ width: '100%', maxWidth: '500px', maxHeight: '70vh', background: theme.bg, borderRadius: '24px 24px 0 0', padding: '20px', overflowY: 'auto' }}>
              <div style={{ width: '40px', height: '4px', background: theme.border, borderRadius: '2px', margin: '0 auto 16px' }} />
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '20px' }}>
                <div style={{ width: '48px', height: '48px', borderRadius: '14px', background: team.color, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '20px', fontWeight: '800', color: '#fff' }}>{team.name.charAt(0)}</div>
                <div>
                  <div style={{ fontSize: '18px', fontWeight: '800', color: theme.text }}>{team.name} Trash Talk</div>
                  <div style={{ fontSize: '13px', color: theme.textSecondary }}>💬 {team.trashTalkCount} {team.trashTalkHot && '🔥'}</div>
                </div>
              </div>
              {team.trashTalkComments.length === 0 ? (
                <div style={{ textAlign: 'center', padding: '32px', color: theme.textSecondary }}>No trash talk yet. Be the first! 🗣️</div>
              ) : (
                team.trashTalkComments.map((c, i) => (
                  <div key={i} style={{ background: theme.bgSecondary, borderRadius: '14px', padding: '14px 16px', marginBottom: '10px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                      <span style={{ fontSize: '12px', color: '#3b82f6', fontWeight: '600' }}>{c.user}</span>
                      <span style={{ fontSize: '12px', color: theme.textMuted }}>❤️ {c.likes}</span>
                    </div>
                    <div style={{ fontSize: '14px', color: theme.text }}>{c.text}</div>
                  </div>
                ))
              )}
              <div style={{ display: 'flex', gap: '10px', marginTop: '16px' }}>
                <input placeholder="Add your trash talk..." style={{ flex: 1, padding: '14px 18px', background: theme.bgSecondary, border: `1px solid ${theme.border}`, borderRadius: '14px', color: theme.text, fontSize: '14px' }} />
                <button style={{ padding: '14px 20px', background: theme.accent, border: 'none', borderRadius: '14px', color: '#fff', fontWeight: '700', cursor: 'pointer' }}>🗣️</button>
              </div>
            </div>
          </div>
        );
      })()}

      {/* GAME DETAIL MODAL */}
      {selectedGame && (
        <div onClick={() => setSelectedGame(null)} style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)', zIndex: 200, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '20px' }}>
          <div onClick={e => e.stopPropagation()} style={{ width: '100%', maxWidth: '460px', maxHeight: '85vh', overflowY: 'auto', background: theme.bg, borderRadius: '20px', padding: '20px', position: 'relative' }}>
            <button onClick={() => setSelectedGame(null)} style={{ position: 'absolute', top: '16px', right: '16px', width: '36px', height: '36px', borderRadius: '10px', background: theme.bgSecondary, border: 'none', color: theme.text, fontSize: '18px', cursor: 'pointer', zIndex: 10 }}>×</button>
            <div style={{ marginBottom: '20px', textAlign: 'center' }}>
              <div style={{ fontSize: '16px', fontWeight: '700', color: theme.text, marginBottom: '4px' }}>{selectedGame.team1} vs {selectedGame.team2}</div>
              <div style={{ fontSize: '13px', color: theme.textSecondary }}>📺 {selectedGame.channel} • {selectedGame.time}</div>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <TeamCard team={getTeamByName(selectedGame.team1)} game={selectedGame} />
              <TeamCard team={getTeamByName(selectedGame.team2)} game={selectedGame} />
            </div>
          </div>
        </div>
      )}

      {/* GRADE INFO MODAL */}
      {showGradeInfo && (
        <div onClick={() => setShowGradeInfo(false)} style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)', zIndex: 200, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '20px' }}>
          <div onClick={e => e.stopPropagation()} style={{ background: theme.bg, borderRadius: '20px', maxWidth: '400px', width: '100%', maxHeight: '80vh', overflow: 'auto' }}>
            <div style={{ padding: '20px', borderBottom: `1px solid ${theme.border}`, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <h2 style={{ margin: 0, fontSize: '20px', fontWeight: '800', color: theme.text }}>How Grades Work</h2>
              <button onClick={() => setShowGradeInfo(false)} style={{ background: 'none', border: 'none', fontSize: '24px', cursor: 'pointer', color: theme.textMuted }}>×</button>
            </div>
            <div style={{ padding: '20px' }}>
              <p style={{ margin: '0 0 20px', fontSize: '14px', color: theme.textSecondary, lineHeight: '1.6' }}>Program grades are calculated from <strong>4 equal pillars</strong>. Each is scored 0-100, then averaged for the final grade.</p>
              {Object.entries(pillarDefinitions).map(([key, pillar]) => (
                <div key={key} style={{ marginBottom: '16px', padding: '16px', background: theme.bgSecondary, borderRadius: '12px', borderLeft: `4px solid ${pillar.color}` }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                    <span style={{ fontSize: '20px' }}>{pillar.icon}</span>
                    <span style={{ fontSize: '16px', fontWeight: '700', color: pillar.color }}>{pillar.name}</span>
                  </div>
                  <p style={{ margin: '0 0 8px', fontSize: '13px', color: theme.textSecondary, lineHeight: '1.5' }}>{pillar.fullDesc}</p>
                  <div style={{ fontSize: '12px', color: theme.textMuted }}><strong>Factors:</strong> {pillar.factors.join(' • ')}</div>
                </div>
              ))}
              <div style={{ marginTop: '20px', padding: '16px', background: '#f0fdf4', borderRadius: '12px', border: '1px solid #bbf7d0' }}>
                <div style={{ fontSize: '14px', fontWeight: '700', color: theme.accent, marginBottom: '6px' }}>Grade Scale</div>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                  {['A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D', 'F'].map(g => (
                    <span key={g} style={{ padding: '4px 8px', background: `${getGradeColor(g)}20`, color: getGradeColor(g), borderRadius: '4px', fontSize: '12px', fontWeight: '700' }}>{g}</span>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* LEGEND MODAL */}
      {showLegend && (
        <div onClick={() => setShowLegend(false)} style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)', zIndex: 200, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '20px' }}>
          <div onClick={e => e.stopPropagation()} style={{ background: theme.bg, borderRadius: '20px', maxWidth: '400px', width: '100%', maxHeight: '80vh', overflow: 'auto' }}>
            <div style={{ padding: '20px', borderBottom: `1px solid ${theme.border}`, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <h2 style={{ margin: 0, fontSize: '20px', fontWeight: '800', color: theme.text }}>📖 Stats Legend</h2>
              <button onClick={() => setShowLegend(false)} style={{ background: 'none', border: 'none', fontSize: '24px', cursor: 'pointer', color: theme.textMuted }}>×</button>
            </div>
            <div style={{ padding: '12px 20px', background: theme.bgSecondary, fontSize: '13px', color: theme.textSecondary }}>💡 Tap any stat with ⓘ for a quick definition</div>
            <div style={{ padding: '20px' }}>
              {Object.entries(statDefinitions).map(([key, def]) => (
                <div key={key} style={{ padding: '12px 0', borderBottom: `1px solid ${theme.border}` }}>
                  <div style={{ fontSize: '14px', fontWeight: '700', color: theme.text, marginBottom: '4px' }}>{def.label}</div>
                  <div style={{ fontSize: '13px', color: theme.textSecondary, lineHeight: '1.4' }}>{def.desc}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      <style>{`
        @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.4; } }
        * { box-sizing: border-box; }
        body { margin: 0; }
        input::placeholder { color: ${theme.textMuted}; }
      `}</style>
    </div>
  );
};

export default GamedayHQ;
