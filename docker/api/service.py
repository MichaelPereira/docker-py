import warnings
from .. import auth, errors, utils
from ..types import ServiceMode


class ServiceApiMixin(object):
    @utils.minimum_version('1.24')
    def create_service(
            self, task_template, name=None, labels=None, mode=None,
            update_config=None, networks=None, endpoint_config=None,
            endpoint_spec=None
    ):
        """
        Create a service.

        Args:
            task_template (TaskTemplate): Specification of the task to start as
                part of the new service.
            name (string): User-defined name for the service. Optional.
            labels (dict): A map of labels to associate with the service.
                Optional.
            mode (ServiceMode): Scheduling mode for the service (replicated
                or global). Defaults to replicated.
            update_config (UpdateConfig): Specification for the update strategy
                of the service. Default: ``None``
            networks (:py:class:`list`): List of network names or IDs to attach
                the service to. Default: ``None``.
            endpoint_spec (EndpointSpec): Properties that can be configured to
                access and load balance a service. Default: ``None``.

        Returns:
            A dictionary containing an ``ID`` key for the newly created
            service.

        Raises:
            :py:class:`docker.errors.APIError`
                If the server returns an error.
        """
        if endpoint_config is not None:
            warnings.warn(
                'endpoint_config has been renamed to endpoint_spec.',
                DeprecationWarning
            )
            endpoint_spec = endpoint_config

        url = self._url('/services/create')
        headers = {}
        image = task_template.get('ContainerSpec', {}).get('Image', None)
        if image is None:
            raise errors.DockerException(
                'Missing mandatory Image key in ContainerSpec'
            )
        if mode and not isinstance(mode, dict):
            mode = ServiceMode(mode)

        registry, repo_name = auth.resolve_repository_name(image)
        auth_header = auth.get_config_header(self, registry)
        if auth_header:
            headers['X-Registry-Auth'] = auth_header
        data = {
            'Name': name,
            'Labels': labels,
            'TaskTemplate': task_template,
            'Mode': mode,
            'UpdateConfig': update_config,
            'Networks': utils.convert_service_networks(networks),
            'EndpointSpec': endpoint_spec
        }
        return self._result(
            self._post_json(url, data=data, headers=headers), True
        )

    @utils.minimum_version('1.24')
    @utils.check_resource
    def inspect_service(self, service):
        """
        Return information about a service.

        Args:
            service (str): Service name or ID

        Returns:
            ``True`` if successful.

        Raises:
            :py:class:`docker.errors.APIError`
                If the server returns an error.
        """
        url = self._url('/services/{0}', service)
        return self._result(self._get(url), True)

    @utils.minimum_version('1.24')
    @utils.check_resource
    def inspect_task(self, task):
        """
        Retrieve information about a task.

        Args:
            task (str): Task ID

        Returns:
            (dict): Information about the task.

        Raises:
            :py:class:`docker.errors.APIError`
                If the server returns an error.
        """
        url = self._url('/tasks/{0}', task)
        return self._result(self._get(url), True)

    @utils.minimum_version('1.24')
    @utils.check_resource
    def remove_service(self, service):
        """
        Stop and remove a service.

        Args:
            service (str): Service name or ID

        Returns:
            ``True`` if successful.

        Raises:
            :py:class:`docker.errors.APIError`
                If the server returns an error.
        """

        url = self._url('/services/{0}', service)
        resp = self._delete(url)
        self._raise_for_status(resp)
        return True

    @utils.minimum_version('1.24')
    def services(self, filters=None):
        """
        List services.

        Args:
            filters (dict): Filters to process on the nodes list. Valid
                filters: ``id`` and ``name``. Default: ``None``.

        Returns:
            A list of dictionaries containing data about each service.

        Raises:
            :py:class:`docker.errors.APIError`
                If the server returns an error.
        """
        params = {
            'filters': utils.convert_filters(filters) if filters else None
        }
        url = self._url('/services')
        return self._result(self._get(url, params=params), True)

    @utils.minimum_version('1.24')
    def tasks(self, filters=None):
        """
        Retrieve a list of tasks.

        Args:
            filters (dict): A map of filters to process on the tasks list.
                Valid filters: ``id``, ``name``, ``service``, ``node``,
                ``label`` and ``desired-state``.

        Returns:
            (:py:class:`list`): List of task dictionaries.

        Raises:
            :py:class:`docker.errors.APIError`
                If the server returns an error.
        """

        params = {
            'filters': utils.convert_filters(filters) if filters else None
        }
        url = self._url('/tasks')
        return self._result(self._get(url, params=params), True)

    @utils.minimum_version('1.24')
    @utils.check_resource
    def update_service(self, service, version, task_template=None, name=None,
                       labels=None, mode=None, update_config=None,
                       networks=None, endpoint_config=None,
                       endpoint_spec=None):
        """
        Update a service.

        Args:
            service (string): A service identifier (either its name or service
                ID).
            version (int): The version number of the service object being
                updated. This is required to avoid conflicting writes.
            task_template (TaskTemplate): Specification of the updated task to
                start as part of the service.
            name (string): New name for the service. Optional.
            labels (dict): A map of labels to associate with the service.
                Optional.
            mode (ServiceMode): Scheduling mode for the service (replicated
                or global). Defaults to replicated.
            update_config (UpdateConfig): Specification for the update strategy
                of the service. Default: ``None``.
            networks (:py:class:`list`): List of network names or IDs to attach
                the service to. Default: ``None``.
            endpoint_spec (EndpointSpec): Properties that can be configured to
                access and load balance a service. Default: ``None``.

        Returns:
            ``True`` if successful.

        Raises:
            :py:class:`docker.errors.APIError`
                If the server returns an error.
        """
        if endpoint_config is not None:
            warnings.warn(
                'endpoint_config has been renamed to endpoint_spec.',
                DeprecationWarning
            )
            endpoint_spec = endpoint_config

        url = self._url('/services/{0}/update', service)
        data = {}
        headers = {}
        if name is not None:
            data['Name'] = name
        if labels is not None:
            data['Labels'] = labels
        if mode is not None:
            if not isinstance(mode, dict):
                mode = ServiceMode(mode)
            data['Mode'] = mode
        if task_template is not None:
            image = task_template.get('ContainerSpec', {}).get('Image', None)
            if image is not None:
                registry, repo_name = auth.resolve_repository_name(image)
                auth_header = auth.get_config_header(self, registry)
                if auth_header:
                    headers['X-Registry-Auth'] = auth_header
            data['TaskTemplate'] = task_template
        if update_config is not None:
            data['UpdateConfig'] = update_config
        if networks is not None:
            data['Networks'] = utils.convert_service_networks(networks)
        if endpoint_spec is not None:
            data['EndpointSpec'] = endpoint_spec

        resp = self._post_json(
            url, data=data, params={'version': version}, headers=headers
        )
        self._raise_for_status(resp)
        return True
