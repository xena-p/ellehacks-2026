import json
from unittest.mock import patch

from django.test import Client, TestCase
from rest_framework.authtoken.models import Token

from .models import (Enemy, GameRun, GameRunSpell, PermanentUpgrade, Player,
                     QuestionAttempt, Questions, Spell, UserPermanentUpgrade)


class APITestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.player = Player.objects.create_user(
            username="islander", password="treasure-123", coins=100, level=2
        )
        self.token = Token.objects.create(user=self.player)
        self.auth = {"HTTP_AUTHORIZATION": f"Token {self.token.key}"}

    def post_json(self, path, data, **headers):
        return self.client.post(path, json.dumps(data), "application/json", **headers)

    def make_run(self, **overrides):
        values = dict(user=self.player, map_level=1, current_hp=80,
                      enemy_name="Debt Dragon", enemy_hp=75, enemy_max_hp=75,
                      enemy_attack_power=10, reward_coins=15)
        values.update(overrides)
        return GameRun.objects.create(**values)

    def make_question(self, **overrides):
        values = dict(level=1, question_text="Which option is the best value?",
                      answer_choices=["Save", "Spend"], correct_answer_index=0,
                      explanation="Saving protects the goal.", source="seed",
                      fingerprint=f"question-{Questions.objects.count()}")
        values.update(overrides)
        return Questions.objects.create(**values)


class AuthenticationRouteTests(APITestCase):
    def test_all_protected_routes_reject_missing_token(self):
        requests = [
            ("get", "/api/player", None),
            ("post", "/api/game/createenemy?name=Crab&level=1", None),
            ("post", "/api/game/start", {"map_level": 1}),
            ("get", "/api/game/1/generate-quiz", None),
            ("post", "/api/game/1/answer", {"selected_index": 0}),
            ("post", "/api/shop/buy-spell?spell_id=1&game_run_id=1", None),
            ("post", "/api/shop/buy-upgrade?upgrade_id=1&game_run_id=1", None),
            ("post", "/api/game/use-spell?game_run_id=1&spell_id=1", None),
            ("delete", "/api/player/delete", None),
            ("patch", "/api/player/username?new_username=new", None),
            ("patch", "/api/player/password?new_password=new-pass", None),
        ]
        for method, path, body in requests:
            with self.subTest(method=method, path=path):
                kwargs = ({"data": json.dumps(body), "content_type": "application/json"}
                          if body is not None else {})
                self.assertEqual(getattr(self.client, method)(path, **kwargs).status_code, 401)

    def test_bearer_token_is_accepted(self):
        response = self.client.get("/api/player",
            HTTP_AUTHORIZATION=f"Bearer {self.token.key}")
        self.assertEqual(response.status_code, 200)

    def test_invalid_token_is_rejected(self):
        response = self.client.get("/api/player",
                                   HTTP_AUTHORIZATION="Token invalid")
        self.assertEqual(response.status_code, 401)


class AccountRouteTests(APITestCase):
    def test_signup_creates_player_and_returns_token(self):
        response = self.post_json("/api/auth/signup",
            {"username": "  new-player  ", "password": "safe-pass"})
        self.assertEqual(response.status_code, 201)
        created = Player.objects.get(username="new-player")
        self.assertEqual(response.json(), {"username": "new-player",
            "token": Token.objects.get(user=created).key})

    def test_signup_rejects_malformed_payload(self):
        response = self.post_json("/api/auth/signup", {"username": "missing-password"})
        self.assertEqual(response.status_code, 422)

    def test_login_returns_existing_token(self):
        response = self.post_json("/api/auth/login",
            {"username": " islander ", "password": "treasure-123"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"username": "islander", "token": self.token.key})

    def test_login_rejects_bad_credentials(self):
        response = self.post_json("/api/auth/login",
            {"username": "islander", "password": "wrong"})
        self.assertEqual(response.status_code, 404)

    def test_get_player_returns_public_state(self):
        response = self.client.get("/api/player", **self.auth)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(),
            {"level": 2, "max_hp": 100, "coins": 100, "wins": 0})

    def test_update_username(self):
        response = self.client.patch("/api/player/username?new_username=captain", **self.auth)
        self.assertEqual(response.status_code, 200)
        self.player.refresh_from_db()
        self.assertEqual(self.player.username, "captain")

    def test_update_password_hashes_new_password(self):
        response = self.client.patch("/api/player/password?new_password=new-secret", **self.auth)
        self.assertEqual(response.status_code, 200)
        self.player.refresh_from_db()
        self.assertTrue(self.player.check_password("new-secret"))
        self.assertNotEqual(self.player.password, "new-secret")

    def test_delete_player_removes_account_and_token(self):
        response = self.client.delete("/api/player/delete", **self.auth)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Player.objects.filter(pk=self.player.pk).exists())
        self.assertFalse(Token.objects.filter(pk=self.token.pk).exists())


class EnemyAndGameRouteTests(APITestCase):
    def test_only_admin_can_create_enemy(self):
        denied = self.client.post("/api/game/createenemy?name=Crab&level=1", **self.auth)
        self.assertEqual(denied.status_code, 403)
        admin = Player.objects.create_superuser("admin", password="admin-pass")
        token = Token.objects.create(user=admin)
        allowed = self.client.post("/api/game/createenemy?name=Crab&level=1",
            HTTP_AUTHORIZATION=f"Token {token.key}")
        self.assertEqual(allowed.status_code, 200)
        self.assertTrue(Enemy.objects.filter(name="Crab", level=1).exists())

    def test_start_game_creates_run_from_enemy_stats(self):
        Enemy.objects.create(name="Budget Beast", level=2)
        response = self.post_json("/api/game/start", {"map_level": 2}, **self.auth)
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual((payload["enemy_name"], payload["enemy_max_hp"],
                          payload["enemy_attack_power"], payload["reward_coins"]),
                         ("Budget Beast", 60, 15, 15))

    def test_start_game_resumes_existing_active_run(self):
        run = self.make_run(map_level=2)
        Enemy.objects.create(name="Unused", level=2)
        response = self.post_json("/api/game/start", {"map_level": 2}, **self.auth)
        self.assertEqual(response.json()["game_run_id"], run.id)
        self.assertEqual(GameRun.objects.filter(user=self.player).count(), 1)

    def test_start_game_rejects_locked_map(self):
        response = self.post_json("/api/game/start", {"map_level": 3}, **self.auth)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["detail"], "Map locked")

    def test_start_game_requires_configured_enemy(self):
        response = self.post_json("/api/game/start", {"map_level": 2}, **self.auth)
        self.assertEqual(response.status_code, 404)

    @patch("game.api.assign_question")
    def test_generate_quiz_returns_only_public_fields(self, assign_question):
        run, question = self.make_run(), self.make_question()
        attempt = QuestionAttempt.objects.create(game_run=run, question=question)
        assign_question.return_value = attempt
        response = self.client.get(f"/api/game/{run.id}/generate-quiz", **self.auth)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"question_id": attempt.id,
            "question": question.question_text, "options": question.answer_choices})
        assign_question.assert_called_once_with(run)

    def test_generate_quiz_cannot_access_another_players_run(self):
        other = Player.objects.create_user("other", password="pass")
        run = GameRun.objects.create(user=other, current_hp=100)
        self.assertEqual(self.client.get(
            f"/api/game/{run.id}/generate-quiz", **self.auth).status_code, 404)


class AnswerRouteTests(APITestCase):
    def make_attempt(self, **run_overrides):
        return QuestionAttempt.objects.create(game_run=self.make_run(**run_overrides),
                                              question=self.make_question())

    def test_correct_answer_damages_enemy_and_records_attempt(self):
        attempt = self.make_attempt(enemy_hp=75)
        response = self.post_json(f"/api/game/{attempt.id}/answer",
                                  {"selected_index": 0}, **self.auth)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["correct"])
        self.assertEqual(response.json()["enemy_hp"], 50)
        attempt.refresh_from_db()
        self.assertIsNotNone(attempt.answered_at)

    def test_incorrect_answer_damages_player(self):
        attempt = self.make_attempt(current_hp=80, enemy_attack_power=10)
        response = self.post_json(f"/api/game/{attempt.id}/answer",
                                  {"selected_index": 1}, **self.auth)
        self.assertFalse(response.json()["correct"])
        self.assertEqual(response.json()["current_hp"], 70)

    def test_invalid_answer_index_returns_400_without_answering(self):
        attempt = self.make_attempt()
        response = self.post_json(f"/api/game/{attempt.id}/answer",
                                  {"selected_index": 99}, **self.auth)
        self.assertEqual(response.status_code, 400)
        attempt.refresh_from_db()
        self.assertIsNone(attempt.answered_at)

    def test_winning_answer_ends_run_and_rewards_player(self):
        attempt = self.make_attempt(enemy_hp=20, reward_coins=15, map_level=2)
        response = self.post_json(f"/api/game/{attempt.id}/answer",
                                  {"selected_index": 0}, **self.auth)
        self.assertEqual(response.json()["outcome"], "won")
        self.assertEqual(response.json()["new_coins"], 115)
        attempt.game_run.refresh_from_db()
        self.player.refresh_from_db()
        self.assertFalse(attempt.game_run.active)
        self.assertEqual(self.player.wins, 1)

    def test_answer_cannot_access_another_players_attempt(self):
        other = Player.objects.create_user("other", password="pass")
        run = GameRun.objects.create(user=other, current_hp=100)
        attempt = QuestionAttempt.objects.create(game_run=run, question=self.make_question())
        response = self.post_json(f"/api/game/{attempt.id}/answer",
                                  {"selected_index": 0}, **self.auth)
        self.assertEqual(response.status_code, 404)


class ShopAndSpellRouteTests(APITestCase):
    def test_buy_upgrade_deducts_coins_and_records_purchase(self):
        upgrade = PermanentUpgrade.objects.create(name="Heart", hp_bonus=20, cost=30)
        response = self.client.post(
            f"/api/shop/buy-upgrade?upgrade_id={upgrade.id}&game_run_id=123", **self.auth)
        self.assertEqual(response.status_code, 200)
        self.player.refresh_from_db()
        self.assertEqual(self.player.coins, 70)
        self.assertTrue(UserPermanentUpgrade.objects.filter(
            user=self.player, upgrade=upgrade).exists())

    def test_buy_upgrade_with_insufficient_coins_does_not_charge(self):
        upgrade = PermanentUpgrade.objects.create(name="Crown", hp_bonus=50, cost=500)
        response = self.client.post(
            f"/api/shop/buy-upgrade?upgrade_id={upgrade.id}&game_run_id=123", **self.auth)
        self.assertEqual(response.status_code, 200)
        self.player.refresh_from_db()
        self.assertEqual(self.player.coins, 100)
        self.assertFalse(UserPermanentUpgrade.objects.filter(user=self.player).exists())

    def test_buy_spell_with_insufficient_coins(self):
        run = self.make_run()
        spell = Spell.objects.create(name="Mega Heal", effect="heal", value=50, cost=500)
        response = self.client.post(
            f"/api/shop/buy-spell?spell_id={spell.id}&game_run_id={run.id}", **self.auth)
        self.assertEqual(response.json(), {"error": "Not enough coins"})

    @patch("game.api.GameRunSpell.objects.get", return_value=None)
    def test_buy_spell_deducts_coins_and_records_purchase(self, _get):
        run = self.make_run()
        spell = Spell.objects.create(name="Small Heal", effect="heal", value=20, cost=25)
        response = self.client.post(
            f"/api/shop/buy-spell?spell_id={spell.id}&game_run_id={run.id}", **self.auth)
        self.assertEqual(response.status_code, 200)
        self.player.refresh_from_db()
        self.assertEqual(self.player.coins, 75)
        self.assertTrue(GameRunSpell.objects.filter(game_run=run, spell=spell).exists())

    @patch("game.api.GameService.use_spell", return_value=95)
    def test_use_spell_returns_updated_hp(self, use_spell):
        response = self.client.post("/api/game/use-spell?game_run_id=7&spell_id=3", **self.auth)
        self.assertEqual(response.json(), {"current_hp": 95})
        use_spell.assert_called_once_with(self.player, 7, 3)


class PlayerAndGameModelTests(TestCase):
    def setUp(self):
        self.player = Player.objects.create_user("model-player", password="pass")

    def test_max_hp_includes_permanent_upgrades(self):
        upgrade = PermanentUpgrade.objects.create(name="Armor", hp_bonus=25, cost=20)
        UserPermanentUpgrade.objects.create(user=self.player, upgrade=upgrade)
        self.assertEqual(self.player.max_hp, 125)

    def test_recalculate_level_uses_thresholds_and_caps_at_five(self):
        for wins, expected in [(0, 1), (1, 2), (2, 3), (3, 4), (99, 5)]:
            with self.subTest(wins=wins):
                self.player.wins = wins
                self.player.save(update_fields=["wins"])
                self.player.recalculate_level()
                self.assertEqual(self.player.level, expected)

    def test_game_run_damage_is_clamped_at_zero(self):
        run = GameRun.objects.create(user=self.player, current_hp=5, enemy_hp=5)
        run.damage_player(10)
        run.damage_enemy(10)
        self.assertEqual((run.current_hp, run.enemy_hp), (0, 0))
        self.assertTrue(run.is_lost())
        self.assertTrue(run.is_won())
