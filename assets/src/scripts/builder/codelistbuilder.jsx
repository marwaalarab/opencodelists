"use strict";

import React from "react";
import Modal from "react-bootstrap/Modal";

import TreeTables from "../common/tree-tables";
import { getCookie } from "../utils";

class CodelistBuilder extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      codeToStatus: props.codeToStatus,
      updateQueue: [],
      updating: false,
      moreInfoModalCode: null,
    };

    this.updateStatus = props.isEditable ? this.updateStatus.bind(this) : null;
    this.showMoreInfoModal = this.showMoreInfoModal.bind(this);
    this.hideMoreInfoModal = this.hideMoreInfoModal.bind(this);
  }

  componentDidMount() {
    // This is required for testing.  See other uses for _isMounted for explanation.
    this._isMounted = true;
  }

  componentWillUnmount() {
    this._isMounted = false;
  }

  updateStatus(code, status) {
    this.setState(({ codeToStatus, updateQueue }, { hierarchy }) => {
      const newCodeToStatus = hierarchy.updateCodeToStatus(
        codeToStatus,
        code,
        status
      );

      return {
        codeToStatus: newCodeToStatus,
        updateQueue: updateQueue.concat([[code, newCodeToStatus[code]]]),
      };
    }, this.maybePostUpdates);
  }

  maybePostUpdates() {
    if (this.state.updating || !this.state.updateQueue.length) {
      return;
    }
    this.setState({ updating: true }, this.postUpdates);
  }

  postUpdates() {
    fetch(this.props.updateURL, {
      method: "POST",
      credentials: "include",
      mode: "same-origin",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
        "X-CSRFToken": getCookie("csrftoken"),
      },
      body: JSON.stringify({ updates: this.state.updateQueue }),
    })
      .then((response) => response.json())
      .then((data) => {
        if (!this._isMounted) {
          // In tests the compenent is unmounted, and this may happen before
          // the promise is resolved.  Calling setState on an unmounted
          // component is a no-op and may indicate a memory leak, so it triggers
          // a warning.  Exiting early here prevents that warning.
          return;
        }

        const lastUpdates = data.updates;

        this.setState(
          (state) => {
            const newUpdateQueue = state.updateQueue.slice(lastUpdates.length);
            return { updating: false, updateQueue: newUpdateQueue };
          },

          this.maybePostUpdates
        );
      });
  }

  showMoreInfoModal(code) {
    this.setState({ moreInfoModalCode: code });
  }

  hideMoreInfoModal() {
    this.setState({ moreInfoModalCode: null });
  }

  counts() {
    let counts = {
      "?": 0,
      "!": 0,
      "+": 0,
      "(+)": 0,
      "-": 0,
      "(-)": 0,
      total: 0,
    };
    this.props.allCodes.forEach((code) => {
      const status = this.state.codeToStatus[code];
      if (["?", "!", "+", "(+)", "-", "(-)"].includes(status)) {
        counts[status] += 1;
        counts["total"] += 1;
      }
    });
    return counts;
  }

  complete() {
    const counts = this.counts();
    return counts["!"] === 0 && counts["?"] === 0;
  }

  render() {
    const moreInfoModal =
      this.state.moreInfoModalCode &&
      this.renderMoreInfoModal(this.state.moreInfoModalCode);

    return (
      <>
        <div className="row">
          <div className="col-md-3 col-lg-2">
            {this.props.isEditable && (
              <>
                <ManagementForm complete={this.complete()} />
                <hr />
              </>
            )}

            <h6>Summary</h6>
            <Filter filter={this.props.filter} />
            <Summary counts={this.counts()} />
            <hr />

            {this.props.searches.length > 0 && (
              <>
                <h6>Searches</h6>
                <div className="list-group">
                  {this.props.searches.map((search) => (
                    <Search key={search.url} search={search} />
                  ))}
                  {this.props.searches.some((search) => search.active) ? (
                    <a
                      href={this.props.draftURL}
                      className="list-group-item list-group-item-action py-1 font-italic"
                    >
                      show all
                    </a>
                  ) : null}
                </div>
                <hr />
              </>
            )}

            {this.props.isEditable && (
              <>
                <h6>New search</h6>
                <SearchForm searchURL={this.props.searchURL} />
                <hr />
              </>
            )}

            <dl>
              <dt>Coding system</dt>
              <dd>{this.props.metadata.coding_system_name}</dd>

              {this.props.metadata.organisation_name ? (
                <>
                  <dt>Organisation</dt>
                  <dd>{this.props.metadata.organisation_name}</dd>
                </>
              ) : null}

              <dt>Codelist ID</dt>
              <dd className="text-break">
                {this.props.metadata.codelist_full_slug}
              </dd>

              <dt>ID</dt>
              <dd>{this.props.metadata.hash}</dd>
            </dl>
            <hr />

            <h6>Versions</h6>
            <ul className="pl-3">
              {this.props.versions.map((version) => (
                <Version key={version.hash} version={version} />
              ))}
            </ul>
          </div>

          <div className="col-9 pl-5">
            <h4>{this.props.resultsHeading}</h4>
            <hr />
            <TreeTables
              codeToStatus={this.state.codeToStatus}
              hierarchy={this.props.hierarchy}
              treeTables={this.props.treeTables}
              codeToTerm={this.props.codeToTerm}
              visiblePaths={this.props.visiblePaths}
              updateStatus={this.updateStatus}
              showMoreInfoModal={this.showMoreInfoModal}
            />
          </div>
        </div>

        {moreInfoModal}
      </>
    );
  }

  renderMoreInfoModal(code) {
    const included = this.props.allCodes.filter(
      (c) => this.state.codeToStatus[c] === "+"
    );
    const excluded = this.props.allCodes.filter(
      (c) => this.state.codeToStatus[c] === "-"
    );
    const significantAncestors = this.props.hierarchy.significantAncestors(
      code,
      included,
      excluded
    );

    const includedAncestorsText = significantAncestors.includedAncestors
      .map((code) => `${this.props.codeToTerm[code]} (${code})`)
      .join(", ");

    const excludedAncestorsText = significantAncestors.excludedAncestors
      .map((code) => `${this.props.codeToTerm[code]} (${code})`)
      .join(", ");

    return (
      <MoreInfoModal
        code={code}
        term={this.props.codeToTerm[code]}
        status={this.state.codeToStatus[code]}
        includedAncestorsText={includedAncestorsText}
        excludedAncestorsText={excludedAncestorsText}
        hideModal={this.hideMoreInfoModal}
      />
    );
  }
}

function ManagementForm(props) {
  const { complete } = props;

  return (
    <form method="post">
      <input
        type="hidden"
        name="csrfmiddlewaretoken"
        value={getCookie("csrftoken")}
      />
      <div className="btn-group-vertical btn-block" role="group">
        {complete ? (
          <button
            type="submit"
            name="action"
            value="save-for-review"
            className="btn btn-outline-primary btn-block"
          >
            Save for review
          </button>
        ) : (
          <button
            type="button"
            className="disabled btn btn-outline-secondary btn-block"
            aria-disabled="true"
            data-toggle="tooltip"
            title="You cannot save for review until all search results are included or excluded"
          >
            Save for review
          </button>
        )}
        <button
          type="submit"
          name="action"
          value="save-draft"
          className="btn btn-outline-primary btn-block"
        >
          Save draft
        </button>
        <button
          type="submit"
          name="action"
          value="discard"
          className="btn btn-outline-primary btn-block"
        >
          Discard
        </button>
      </div>
    </form>
  );
}

function Filter(props) {
  const { filter } = props;
  return filter ? (
    <p>Filtered to {filter} concepts and their descendants.</p>
  ) : null;
}

function Search(props) {
  const { search } = props;

  return search.delete_url ? (
    <form method="post" action={search.delete_url} className="mt-0 pt-0">
      <input
        type="hidden"
        name="csrfmiddlewaretoken"
        value={getCookie("csrftoken")}
      />

      <a
        href={search.url}
        className={
          search.active
            ? "list-group-item list-group-item-action active py-1 px-2"
            : "list-group-item list-group-item-action py-1 px-2 "
        }
      >
        {search.term_or_code}

        <button
          type="submit"
          name="delete-search"
          className="btn badge badge-secondary float-right"
        >
          x
        </button>
      </a>
    </form>
  ) : (
    <a
      href={search.url}
      className={
        search.active
          ? "list-group-item list-group-item-action active py-1 px-2"
          : "list-group-item list-group-item-action py-1 px-2 "
      }
    >
      {search.term_or_code}
    </a>
  );
}

function Version(props) {
  const { version } = props;

  return (
    <li>
      {version.current ? (
        version.tag_or_hash
      ) : (
        <a href={version.url}>{version.tag_or_hash}</a>
      )}

      {version.status === "draft" ? (
        <>
          {" "}
          <span className="badge badge-primary">Draft</span>
        </>
      ) : null}

      {version.status === "under review" ? (
        <>
          {" "}
          <span className="badge badge-primary">Review</span>
        </>
      ) : null}
    </li>
  );
}

function SearchForm(props) {
  const { searchURL } = props;

  return (
    <form method="post" action={searchURL}>
      <div className="form-group">
        <input
          type="hidden"
          name="csrfmiddlewaretoken"
          value={getCookie("csrftoken")}
        />
        <input
          type="search"
          className="form-control"
          name="search"
          placeholder="Term or code"
        />
      </div>
      <div>
        <button
          type="submit"
          name="field"
          className="btn btn-sm btn-primary mr-1"
        >
          Search
        </button>
      </div>
      <div>
        <small className="form-text text-muted">
          <p>
            To search by code, prefix your search with <code>code:</code>. For
            instance, use <code>code:xyz</code> to find the concept with code{" "}
            <code>xyz</code>, or <code>code:xyz*</code> to find all concepts
            with codes beginning <code>xyz</code>.
          </p>
          <p>
            Otherwise, searching will return all concepts with a description
            containing the search term.
          </p>
          <p>
            We plan to support boolean search operators (eg{" "}
            <code>ambulatory AND blood pressure</code>) in future.
          </p>
        </small>
      </div>
    </form>
  );
}

function MoreInfoModal(props) {
  const {
    code,
    term,
    status,
    includedAncestorsText,
    excludedAncestorsText,
    hideModal,
  } = props;

  let text = null;

  switch (status) {
    case "+":
      text = "Included";
      break;
    case "(+)":
      text = `Included by ${includedAncestorsText}`;
      break;
    case "-":
      text = "Excluded";
      break;
    case "(-)":
      text = `Excluded by ${includedAncestorsText}`;
      break;
    case "?":
      text = "Unresolved";
      break;
    case "!":
      text = `In conflict!  Included by ${includedAncestorsText}, and excluded by ${excludedAncestorsText}`;
      break;
  }

  return (
    <Modal show={code !== null} onHide={hideModal} centered>
      <Modal.Header closeButton>
        {term} ({code})
      </Modal.Header>
      <Modal.Body>{text}</Modal.Body>
    </Modal>
  );
}

function Summary(props) {
  return (
    <>
      <p>
        Found <span id="summary-total">{props.counts.total}</span> matching
        concepts (including descendants).
      </p>
      {props.counts["+"] > 0 && (
        <p>
          <span id="summary-included">
            {props.counts["+"] + props.counts["(+)"]}
          </span>{" "}
          have been <a href="?filter=included">included</a> in the codelist.
        </p>
      )}
      {props.counts["-"] > 0 && (
        <p>
          <span id="summary-excluded">
            {props.counts["-"] + props.counts["(-)"]}
          </span>{" "}
          have been <a href="?filter=excluded">excluded</a> from the codelist.
        </p>
      )}
      {props.counts["?"] > 0 && (
        <p>
          <span id="summary-unresolved">{props.counts["?"]}</span> are{" "}
          <a href="?filter=unresolved">unresolved</a>.
        </p>
      )}
      {props.counts["!"] > 0 && (
        <p>
          <span id="summary-in-conflict">{props.counts["!"]}</span> are{" "}
          <a href="?filter=in-conflict">in conflict</a>.
        </p>
      )}
    </>
  );
}

export { CodelistBuilder as default };
