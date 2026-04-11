"""Flappy Pitch — entry point."""

from src.game import Game


def main() -> None:
    """Run Flappy Pitch."""
    game: Game = Game()
    game.run()


if __name__ == "__main__":
    main()
