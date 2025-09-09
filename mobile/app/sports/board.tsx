import SportsBoardScreen from './SportsBoardScreen';

// NCAAF-specific board that uses the unified SportsBoardScreen
export default function NCAAfBoardScreen() {
  return <SportsBoardScreen initialLeagueId="NCAAF" />;
}