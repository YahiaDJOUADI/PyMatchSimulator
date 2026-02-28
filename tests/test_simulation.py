import unittest
import os
import json
from models.player import Player
from models.team import Team
from models.match import Match
from engine.simulator import SimulatorEngine
from utils.history_manager import save_match_history, update_career_stats

class TestSimulation(unittest.TestCase):
    def setUp(self):
        self.p1 = Player("Lionel Messi", "FW", 94, age=36, stamina=100)
        self.p2 = Player("Cristiano Ronaldo", "FW", 93, age=39, stamina=100)
        self.p3 = Player("Ter Stegen", "GK", 89, age=31, stamina=100)
        self.p4 = Player("Neuer", "GK", 89, age=37, stamina=100)
        
        self.team1 = Team("Barcelona Legends", 90, 85, 88, [self.p1, self.p3])
        self.team2 = Team("Madrid Legends", 89, 86, 87, [self.p2, self.p4])

        self.test_history_file = "data/test_matches.json"
        self.test_stats_file = "data/test_stats.json"

    def tearDown(self):
        if os.path.exists(self.test_history_file):
            os.remove(self.test_history_file)
        if os.path.exists(self.test_stats_file):
            os.remove(self.test_stats_file)

    def test_full_match_simulation(self):
        match = Match(self.team1, self.team2)
        engine = SimulatorEngine(match)
        
        engine.simulate_match()
        
        self.assertTrue(len(match.events) > 0, "No events were generated.")
        self.assertIsNotNone(match.man_of_match, "Man of the match was not assigned.")
        self.assertTrue(match.team1.matches_played > 0, "Matches played stat was not updated.")

    def test_history_manager(self):
        match = Match(self.team1, self.team2)
        match.score1 = 2
        match.score2 = 1
        self.p1.goals = 2 
        self.p2.goals = 1
        match.finalize_match()
        
        save_match_history(match, self.test_history_file)
        self.assertTrue(os.path.exists(self.test_history_file))
        
        with open(self.test_history_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.assertEqual(len(data['matches']), 1)
            self.assertEqual(data['matches'][0]['score1'], 2)

        update_career_stats(match, self.test_stats_file)
        self.assertTrue(os.path.exists(self.test_stats_file))
        
        with open(self.test_stats_file, 'r', encoding='utf-8') as f:
            stats = json.load(f)
            self.assertEqual(stats['scorers']['Lionel Messi'], 2)
            self.assertEqual(stats['scorers']['Cristiano Ronaldo'], 1)

if __name__ == "__main__":
    unittest.main()
