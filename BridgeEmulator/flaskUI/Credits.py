from flask_restful import Resource
from typing import Union, List, Dict, Any, Tuple

class Credits(Resource):
    def get(self, resource: str) -> Union[List[Dict[str, Any]], Tuple[str, int]]:
        """
        Handle GET requests for various resources.

        Args:
            resource (str): The name of the resource being requested.

        Returns:
            Union[List[Dict[str, Any]], Tuple[str, int]]: The response data for the requested resource,
            or a 404 status code if the resource is not found.
        """
        json_responses = {
            "packages.json": [
                {
                    "Attributions": [],
                    "SPDX-License-Identifiers": [""],
                    "SourceLinks": ["https://github.com/mariusmotea"],
                    "licenses": {"Main Developer & Mastermind of DiyHue": "Marius.txt"},
                    "Version": "",
                    "Package": "Marius",
                    "Website": "https://github.com/mariusmotea"
                },
                {
                    "Attributions": [],
                    "SPDX-License-Identifiers": [""],
                    "SourceLinks": ["https://github.com/cheesemarathon"],
                    "licenses": {"Github & CI/CD Wizard": "cheesemarathon.txt"},
                    "Version": "",
                    "Package": "cheesemarathon",
                    "Website": "https://github.com/cheesemarathon"
                },
                {
                    "Attributions": [],
                    "SPDX-License-Identifiers": [""],
                    "SourceLinks": ["https://github.com/Mevel"],
                    "licenses": {"Maintainer & Support": "Mevel.txt"},
                    "Version": "",
                    "Package": "Mevel",
                    "Website": "https://github.com/Mevel"
                },
                {
                    "Attributions": [],
                    "SPDX-License-Identifiers": [""],
                    "SourceLinks": ["https://github.com/fisico"],
                    "licenses": {"Designed and developed the user interface": "David.txt"},
                    "Version": "",
                    "Package": "David",
                    "Website": "https://github.com/fisico"
                },
                {
                    "Attributions": [],
                    "SPDX-License-Identifiers": [""],
                    "SourceLinks": ["https://github.com/philharmonie"],
                    "licenses": {"React consultant": "Phil.txt"},
                    "Version": "",
                    "Package": "Phil",
                    "Website": "https://github.com/philharmonie"
                },
                {
                    "Attributions": [],
                    "SPDX-License-Identifiers": [""],
                    "SourceLinks": ["https://github.com/hendriksen-mark"],
                    "licenses": {"Maintainer & Support": "Mark.txt"},
                    "Version": "",
                    "Package": "Mark",
                    "Website": "https://github.com/hendriksen-mark"
                },
                {
                    "Attributions": [],
                    "SPDX-License-Identifiers": [""],
                    "SourceLinks": ["https://github.com/diyhue/diyHue/graphs/contributors"],
                    "licenses": {"A big thank you to everyone contributing to this project": "contributors.txt"},
                    "Version": "",
                    "Package": "Thank you!",
                    "Website": "https://github.com/diyhue/diyHue/graphs/contributors"
                }
            ],
            "hardcoded.json": [
                {
                    "Attributions": [],
                    "SPDX-License-Identifiers": [""],
                    "SourceLinks": ["https://github.com/diyhue/diyHue"],
                    "licenses": {"Main diyHue software repo": "DiyHue.txt"},
                    "Version": "",
                    "Package": "DiyHue",
                    "Website": "https://github.com/diyhue/diyHue"
                }
            ],
            "rust-packages.json": [
                {
                    "Attributions": [],
                    "SPDX-License-Identifiers": [""],
                    "SourceLinks": ["https://github.com/diyhue"],
                    "licenses": {"diyHue repositories": "Repositories.txt"},
                    "Version": "",
                    "Package": "DiyHue Repositories",
                    "Website": "https://github.com/diyhue"
                }
            ]
        }

        text_responses = {
            "Marius.txt": "Marius. Main Developer & Mastermind of DiyHue. Developing and maintaining basically everything. Thousands of hours spent for reverse engineering, bug fixing and trying to implement every possible feature in his project.",
            "cheesemarathon.txt": "Cheesemarathon. Github & CI/CD Wizard. Created and maintaining the Github repository, Docker images and Github actions.",
            "Mevel.txt": "Mevel. Maintainer & Support. Maintaining the website, taking care of the community and running Slack are only a small portion of his efforts he invests into the project.",
            "David.txt": "David. Designed and developed the user interface. Designed and frontend developed the user interface and user experience. Design and producing music (Spaceflight Memories Music https://spaceflightmemories.com/) is, what his life is all about.",
            "Phil.txt": "Phil. React consultant. A very special thank you to Phil for consulting us with everything React related.",
            "Mark.txt": "Mark. Maintainer & Support. Maintaining the Github repository, Add api features, Fix bugs, Slack & Github support.",
            "contributors.txt": "A big thank you to everyone contributing to this project: mariusmotea, BB-BenBridges, juanesf, alexyao2015, hendriksen-mark, zwegner, jdaandersj, SilveIT, jespertheend, MunkeyBalls, cad435, ticed35, snyk-bot, shbatm, n3PH1lim, Mevel, J3n50m4t, camatthew, mcer12, shivasiddharth, Nikfinn99, Fisico, avinashraja98, memen45, kurniawan77, foxy82, sosheskaz, igorcv88, julian-margara, Paalap, Petapton, scubiedoo, 7FM, falkena, cwildfoerster, Animii, maberle, rkkoszewski, Pantastisch, subnoize417, standardgateway, obelix05, dependabot[bot], vlad-the-compiler, sneak-thief, maxbec, j-simian, jamesremuscat, imcfarla2003, GitHobi, casab, freddebo, fmoo1409, downace, betonishard, basktrading, Wqrld, TopdRob, pecirep, Timoms, timbru31, ghostekpl, SacerSors, andriymoroz, hre999, inukiwi, Infactionfreddy, loefkvist, malt3, mattisz, mcrummett, mreijnde, srd424, Thomas-Vos, xieve, yavadan, zejjnt, t-anjan, fazledyn-or, adrum, daborbor, chrisbraucker, cuthbertnibbles, dfloer, device111, ElliotSmith91, FezVrasta, gbotti, GerdZanker, ImgBotApp, bauerj, Jokeronomy, Kitula, legovaer, marcelkordek, maxcanna, MrSuttonmann, oleg2204, PapACutA, rernst",
            "DiyHue.txt": "https://github.com/diyhue/diyHue",
            "Repositories.txt": "https://github.com/diyhue"
        }

        if resource in json_responses:
            return json_responses[resource]
        elif resource in text_responses:
            return text_responses[resource]
        else:
            return "Resource not found", 404
