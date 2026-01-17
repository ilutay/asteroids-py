import asyncio
import logging

from game import Game

# Configure logging for the game client
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)


async def main() -> None:
    game = Game()
    await game.run()


asyncio.run(main())
