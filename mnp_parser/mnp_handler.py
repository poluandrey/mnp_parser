from mnp_parser import latvia_mnp


def parser(country: str) -> None:
    if country == 'latvia':
        latvia_mnp.parse()


if __name__ == '__main__':
    parser()
