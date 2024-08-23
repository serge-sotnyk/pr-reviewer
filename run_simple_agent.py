from dotenv import load_dotenv

from pr_reviewer.simple_reviewer import make_review

load_dotenv()


def main():
    review = make_review(".", "main", "dev")
    print("Review:")
    print(review)


if __name__ == "__main__":
    main()
